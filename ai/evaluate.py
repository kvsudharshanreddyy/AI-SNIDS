"""
ai/evaluate.py

Model evaluation for AI-SNIDS.

Why multiple metrics?
---------------------
In cybersecurity, ACCURACY ALONE IS MISLEADING.

Example: If 95% of traffic is benign, a model that predicts
"BENIGN" for everything achieves 95% accuracy — but detects
ZERO attacks (0% recall on attack classes). This is useless.

Therefore we evaluate:

  PRECISION: Of all traffic flagged as an attack, what fraction
             actually is an attack? High precision = fewer false alarms.

  RECALL:    Of all actual attacks, what fraction did we catch?
             High recall = fewer missed threats (missed detections).

  F1 SCORE:  Harmonic mean of precision and recall — a balanced
             metric that penalizes models that sacrifice one for the other.

  CONFUSION MATRIX: Shows exactly which classes are confused with each
                    other, helping diagnose specific weaknesses.

For an IDS, RECALL is typically more important than PRECISION:
missing a real attack (false negative) is more dangerous than
raising a false alarm (false positive) — though too many false
positives cause alert fatigue in real SOC environments.
"""

import json
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — avoids display requirement
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# ─── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "ai" / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
    model_name: str = "Model",
    feature_names: Optional[list[str]] = None,
    model_dir: Path = MODEL_DIR,
) -> dict:
    """
    Evaluate a trained classifier and save metrics + plots.

    Returns:
        dict with accuracy, precision, recall, f1_macro, f1_weighted,
             confusion_matrix (list), classification_report (str)
    """
    # ── Predictions ────────────────────────────────────────────
    y_pred = model.predict(X_test)

    # ── Core Metrics ───────────────────────────────────────────
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    report = classification_report(
        y_test, y_pred, target_names=class_names, zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred)

    # ── Print to console ───────────────────────────────────────
    print(f"\n{'─' * 50}")
    print(f"Evaluation: {model_name}")
    print(f"{'─' * 50}")
    print(f"  Accuracy  : {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print(f"  Precision : {precision:.4f} (macro)")
    print(f"  Recall    : {recall:.4f} (macro)")
    print(f"  F1 (macro): {f1_macro:.4f}")
    print(f"  F1 (wtd.) : {f1_weighted:.4f}")
    print(f"\nClassification Report:\n{report}")

    # ── Save metrics JSON ──────────────────────────────────────
    results = {
        "model_name": model_name,
        "accuracy": float(accuracy),
        "precision_macro": float(precision),
        "recall_macro": float(recall),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
        "classification_report": report,
    }

    metrics_path = model_dir / f"{model_name.lower()}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[EVAL] Metrics saved: {metrics_path.name}")

    # ── Plot Confusion Matrix ──────────────────────────────────
    _plot_confusion_matrix(cm, class_names, model_name, model_dir)

    # ── Plot Feature Importance (if available) ─────────────────
    if hasattr(model, "feature_importances_") and feature_names:
        _plot_feature_importance(
            model.feature_importances_, feature_names, model_name, model_dir
        )

    return results


def _plot_confusion_matrix(
    cm: np.ndarray,
    class_names: list[str],
    model_name: str,
    save_dir: Path,
) -> None:
    """Generate and save a normalized confusion matrix heatmap."""
    # Normalize by true class totals (row-wise)
    cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)
    cm_norm = np.nan_to_num(cm_norm)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for ax, data, title, fmt in [
        (axes[0], cm, "Counts", "d"),
        (axes[1], cm_norm, "Normalized (row %)", ".2f"),
    ]:
        sns.heatmap(
            data,
            annot=True,
            fmt=fmt,
            cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names,
            ax=ax,
            linewidths=0.5,
        )
        ax.set_title(f"{model_name} — Confusion Matrix ({title})", fontsize=13)
        ax.set_ylabel("True Label", fontsize=11)
        ax.set_xlabel("Predicted Label", fontsize=11)
        ax.tick_params(axis="x", rotation=30)
        ax.tick_params(axis="y", rotation=0)

    plt.tight_layout()
    path = save_dir / f"{model_name.lower()}_confusion_matrix.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[EVAL] Confusion matrix saved: {path.name}")


def _plot_feature_importance(
    importances: np.ndarray,
    feature_names: list[str],
    model_name: str,
    save_dir: Path,
    top_n: int = 15,
) -> None:
    """Generate and save a horizontal bar chart of top-N feature importances."""
    indices = np.argsort(importances)[::-1][:top_n]
    top_names = [feature_names[i] for i in indices]
    top_values = importances[indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, top_n))
    ax.barh(range(top_n), top_values[::-1], color=colors[::-1], edgecolor="white")
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_names[::-1], fontsize=9)
    ax.set_xlabel("Importance Score", fontsize=11)
    ax.set_title(f"{model_name} — Top {top_n} Feature Importances", fontsize=13)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    path = save_dir / f"{model_name.lower()}_feature_importance.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[EVAL] Feature importance chart saved: {path.name}")


def load_metrics(model_name: str, model_dir: Path = MODEL_DIR) -> Optional[dict]:
    """Load previously saved evaluation metrics from JSON."""
    path = model_dir / f"{model_name.lower()}_metrics.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)
