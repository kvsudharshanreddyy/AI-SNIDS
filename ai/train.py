"""
ai/train.py

Random Forest training pipeline for AI-SNIDS.

Why Random Forest?
------------------
1. TABULAR DATA: Network traffic features are tabular (fixed-width rows).
   Random Forest is one of the best algorithms for tabular data — it handles
   mixed feature scales, non-linear relationships, and missing patterns well.

2. INTERPRETABLE: Feature importances tell us exactly which traffic metrics
   the model found most discriminating — directly useful for IDS explanation.

3. CPU-FRIENDLY: Trains fast on 50K–100K rows even on a laptop CPU.
   No GPU required, no special hardware.

4. HANDLES CLASS IMBALANCE: class_weight='balanced' automatically adjusts
   for unequal class frequencies without needing SMOTE or resampling.

5. ROBUST: Ensemble of decision trees — less prone to overfitting than a
   single tree, naturally handles irrelevant features by averaging them out.

6. WELL-ESTABLISHED: Used in many published network IDS papers as a strong
   baseline, making it academically well-justified.

Usage:
    python ai/train.py
"""

import json
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression

# Import our preprocessing pipeline
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.preprocess import preprocess, DATA_DIR, MODEL_DIR
from ai.evaluate import evaluate_model

# ─── Model Configuration ───────────────────────────────────────────────────────

RF_CONFIG = {
    # Number of trees: 100 is a reliable sweet-spot for tabular data.
    # More trees → diminishing returns in accuracy, more training time.
    "n_estimators": 100,

    # Max depth: None lets trees grow fully. We set it to reduce overfitting
    # and keep the model explainable.
    "max_depth": 20,

    # Minimum samples to split a node: helps prevent over-fitting on small
    # leaf nodes.
    "min_samples_split": 5,

    # class_weight='balanced': addresses class imbalance by automatically
    # weighting minority classes higher during training.
    "class_weight": "balanced",

    # Feature sampling per tree: 'sqrt' is the classic RF default for
    # classification — each tree sees sqrt(n_features) at each split.
    "max_features": "sqrt",

    "n_jobs": -1,       # Use all CPU cores
    "random_state": 42,
    "verbose": 1,
}


def train_random_forest(data: dict) -> RandomForestClassifier:
    """Train the primary Random Forest classifier."""
    print("\n" + "=" * 60)
    print("Training: Random Forest Classifier")
    print("=" * 60)

    rf = RandomForestClassifier(**RF_CONFIG)

    t0 = time.time()
    rf.fit(data["X_train"], data["y_train"])
    t1 = time.time()

    print(f"\n[TRAIN] Training completed in {t1 - t0:.1f} seconds")
    print(f"[TRAIN] Trees trained: {rf.n_estimators}")
    print(f"[TRAIN] Feature count: {rf.n_features_in_}")

    return rf


def train_baseline_logreg(data: dict) -> LogisticRegression:
    """
    Train a Logistic Regression baseline for comparison.

    Why compare?
    -----------
    Having a simple baseline (Logistic Regression) lets us verify that
    the Random Forest is genuinely adding value over a linear model.
    If LR performs similarly, the data may be linearly separable and
    RF is overkill. If RF significantly outperforms LR, the non-linear
    decision boundaries in network traffic are confirmed.

    In practice on CICIDS2017, RF typically outperforms LR by 5–15%
    on attack classes like DoS and PortScan.
    """
    print("\n" + "=" * 60)
    print("Training: Logistic Regression (Baseline)")
    print("=" * 60)

    lr = LogisticRegression(
        max_iter=500,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    t0 = time.time()
    lr.fit(data["X_train"], data["y_train"])
    t1 = time.time()

    print(f"[TRAIN] Logistic Regression training: {t1 - t0:.1f}s")
    return lr


def save_model(model, model_dir: Path, filename: str) -> Path:
    """Serialize a trained model using joblib."""
    path = model_dir / filename
    joblib.dump(model, path)
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"[SAVE] {filename} → {size_mb:.1f} MB")
    return path


def save_training_metadata(data: dict, model_dir: Path) -> None:
    """Save training metadata for reproducibility."""
    meta = {
        "model_type": "RandomForestClassifier",
        "n_estimators": RF_CONFIG["n_estimators"],
        "max_depth": RF_CONFIG["max_depth"],
        "class_weight": RF_CONFIG["class_weight"],
        "n_features": len(data["feature_names"]),
        "feature_names": data["feature_names"],
        "class_names": data["class_names"],
        "train_samples": int(len(data["X_train"])),
        "test_samples": int(len(data["X_test"])),
    }
    with open(model_dir / "model_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    print("[SAVE] model_metadata.json")


def main():
    print("=" * 60)
    print("AI-SNIDS: Model Training Pipeline")
    print("=" * 60)

    # ── Phase 1: Preprocess ────────────────────────────────────
    data = preprocess()

    # ── Phase 2: Train primary model ───────────────────────────
    rf_model = train_random_forest(data)

    # ── Phase 3: Evaluate primary model ───────────────────────
    print("\n--- Evaluating Random Forest ---")
    rf_results = evaluate_model(
        model=rf_model,
        X_test=data["X_test"],
        y_test=data["y_test"],
        class_names=data["class_names"],
        model_name="RandomForest",
        feature_names=data["feature_names"],
        model_dir=MODEL_DIR,
    )

    # ── Phase 4: Train baseline model ──────────────────────────
    lr_model = train_baseline_logreg(data)

    print("\n--- Evaluating Logistic Regression (Baseline) ---")
    lr_results = evaluate_model(
        model=lr_model,
        X_test=data["X_test"],
        y_test=data["y_test"],
        class_names=data["class_names"],
        model_name="LogisticRegression",
        feature_names=data["feature_names"],
        model_dir=MODEL_DIR,
    )

    # ── Phase 5: Save models ───────────────────────────────────
    print("\n[SAVE] Saving models...")
    save_model(rf_model, MODEL_DIR, "rf_model.pkl")
    save_model(lr_model, MODEL_DIR, "lr_model.pkl")
    save_training_metadata(data, MODEL_DIR)

    # ── Phase 6: Summary ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"  Random Forest  — Accuracy: {rf_results['accuracy']:.4f}  |  F1 (macro): {rf_results['f1_macro']:.4f}")
    print(f"  Logistic Reg.  — Accuracy: {lr_results['accuracy']:.4f}  |  F1 (macro): {lr_results['f1_macro']:.4f}")

    winner = "Random Forest" if rf_results["f1_macro"] >= lr_results["f1_macro"] else "Logistic Regression"
    print(f"\n  ★ Best model: {winner}")
    print(f"  Model artifacts saved to: {MODEL_DIR}/")
    print("\n[DONE] Training pipeline complete.\n")

    return rf_model, data


if __name__ == "__main__":
    main()
