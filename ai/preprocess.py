"""
ai/preprocess.py

Data preprocessing pipeline for the CICIDS2017 network traffic dataset.

Pipeline:
    Raw CSV files
        → Load & concatenate
        → Column name normalization
        → Attack label mapping
        → Class filtering (only our 5 target classes)
        → Missing value / infinity handling
        → Class sampling (balance + limit per-class rows)
        → Feature selection (top N features based on variance/importance)
        → Train/Test split
        → Feature scaling (StandardScaler)
        → Save artifacts (scaler, feature names, label encoder)

Why these preprocessing steps?
-------------------------------
Network traffic datasets are notoriously messy:
- Column names have leading/trailing spaces (CICIDS2017 quirk)
- Infinity values appear in ratio features (division by near-zero durations)
- Some classes are massively over-represented (BENIGN >> attacks)
- Many features are redundant or zero-variance

Handling all of these improves model quality and prevents training errors.
"""

import json
import os
import warnings
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

warnings.filterwarnings("ignore")

# ─── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "ai" / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ─── CICIDS2017 Dataset Files ───────────────────────────────────────────────────

# These are the CSV files we expect to find in data/
# Each file maps to which attack classes it contains
CICIDS_FILES = {
    "Tuesday-WorkingHours.pcap_ISCX.csv": ["BENIGN", "FTP-Patator", "SSH-Patator"],
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv": ["BENIGN", "DDoS"],
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv": ["BENIGN", "PortScan"],
    "Wednesday-workingHours.pcap_ISCX.csv": [
        "BENIGN", "DoS Hulk", "DoS GoldenEye",
        "DoS slowloris", "DoS Slowhttptest"
    ],
}

# ─── Label Mapping ─────────────────────────────────────────────────────────────

# Map raw CICIDS2017 labels → our 5 unified attack classes
LABEL_MAP = {
    "BENIGN": "BENIGN",
    "FTP-Patator": "BruteForce",
    "SSH-Patator": "BruteForce",
    "DDoS": "DDoS",
    "PortScan": "PortScan",
    "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS",
    "DoS slowloris": "DoS",
    "DoS Slowhttptest": "DoS",
    "Bot": "Botnet",
    "Web Attack  Brute Force": "BruteForce",
    "Web Attack  XSS": "BruteForce",
}

# Our final target classes
TARGET_CLASSES = ["BENIGN", "DoS", "DDoS", "PortScan", "BruteForce"]

# ─── Feature Configuration ─────────────────────────────────────────────────────

# Max rows per class to keep (prevents memory issues on constrained laptops)
MAX_ROWS_PER_CLASS = int(os.getenv("MAX_ROWS_PER_CLASS", "20000"))

# Number of top features to select
N_FEATURES = 20

# The CICIDS2017 label column (has a leading space — a known quirk)
LABEL_COL_CANDIDATES = [" Label", "Label", "label", " label"]

# Features to always exclude (IDs, not signals)
EXCLUDE_COLS = [
    "Flow ID", " Flow ID", "Source IP", " Source IP",
    "Destination IP", " Destination IP", "Timestamp", " Timestamp",
]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all column names."""
    df.columns = df.columns.str.strip()
    return df


def find_label_column(df: pd.DataFrame) -> str:
    """Detect which column holds the traffic labels."""
    for col in LABEL_COL_CANDIDATES:
        if col.strip() in df.columns or col in df.columns:
            return col.strip() if col.strip() in df.columns else col
    raise ValueError(
        f"Could not find label column. Available columns: {list(df.columns[:5])}"
    )


def load_cicids_files(data_dir: Path) -> Optional[pd.DataFrame]:
    """
    Load and concatenate CICIDS2017 CSV files found in data_dir.

    Returns None if no valid files found.
    Prints a warning for each missing file (not all files are required).
    """
    frames = []
    found_any = False

    for filename in CICIDS_FILES:
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"  [INFO] File not found (optional): {filename}")
            continue

        print(f"  [LOAD] Reading {filename} ...")
        try:
            df = pd.read_csv(filepath, low_memory=False)
            df = normalize_columns(df)
            frames.append(df)
            found_any = True
            print(f"         Rows: {len(df):,}  |  Columns: {len(df.columns)}")
        except Exception as e:
            print(f"  [WARN] Failed to read {filename}: {e}")

    if not found_any:
        return None

    combined = pd.concat(frames, ignore_index=True)
    print(f"\n  [LOAD] Combined dataset: {len(combined):,} rows")
    return combined


def clean_data(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    """
    Clean raw network traffic data:

    1. Replace infinity values with NaN
    2. Drop rows with NaN in features
    3. Map raw labels to unified classes
    4. Filter to target classes only
    5. Drop excluded columns (IPs, flow IDs)
    """
    print("\n[CLEAN] Starting data cleaning...")

    # Step 1: Handle infinities (common in ratio-based features)
    n_inf = np.isinf(df.select_dtypes(include=[np.number])).sum().sum()
    if n_inf > 0:
        print(f"  [CLEAN] Replacing {n_inf:,} infinity values with NaN")
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Step 2: Drop rows with any NaN in numeric columns
    n_before = len(df)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df.dropna(subset=numeric_cols, inplace=True)
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        print(f"  [CLEAN] Dropped {n_dropped:,} rows with NaN values")

    # Step 3: Map labels
    df["label_raw"] = df[label_col].astype(str).str.strip()
    df["label"] = df["label_raw"].map(LABEL_MAP)

    unmapped = df["label"].isna().sum()
    if unmapped > 0:
        unique_unmapped = df.loc[df["label"].isna(), "label_raw"].unique()
        print(f"  [CLEAN] Dropping {unmapped:,} rows with unmapped labels: {unique_unmapped}")
    df.dropna(subset=["label"], inplace=True)

    # Step 4: Filter to our target classes
    df = df[df["label"].isin(TARGET_CLASSES)].copy()
    print(f"  [CLEAN] Rows after class filter: {len(df):,}")

    # Step 5: Drop non-feature columns
    cols_to_drop = [c for c in EXCLUDE_COLS if c in df.columns]
    cols_to_drop += ["label_raw", label_col]
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    df.drop(columns=cols_to_drop, inplace=True)

    print(f"  [CLEAN] Final shape: {df.shape}")
    return df


def sample_balanced(df: pd.DataFrame, max_per_class: int) -> pd.DataFrame:
    """
    Sample up to max_per_class rows from each class.

    Why balance?
    -----------
    CICIDS2017 is heavily imbalanced: BENIGN traffic makes up 80%+ of the
    dataset. Training on imbalanced data makes the model biased toward the
    majority class. By sampling equally, we give the model equal exposure
    to each attack type.

    Note: This is random undersampling — a simple and effective strategy
    for our prototype. More advanced approaches (SMOTE, class weights) are
    optional future improvements.
    """
    print("\n[SAMPLE] Balancing classes...")
    frames = []
    for cls in df["label"].unique():
        cls_df = df[df["label"] == cls]
        n = min(len(cls_df), max_per_class)
        sampled = cls_df.sample(n=n, random_state=42)
        frames.append(sampled)
        print(f"  {cls:<15}: {len(cls_df):>8,} → sampled {n:>6,}")
    return pd.concat(frames, ignore_index=True)


def select_features(df: pd.DataFrame, n_features: int) -> list[str]:
    """
    Select the top N features by variance.

    Why variance-based selection?
    ------------------------------
    Features with near-zero variance are useless for classification —
    they carry no discriminating information. Removing them reduces:
    - Training time
    - Model complexity
    - Risk of overfitting

    For a more sophisticated selection, a fitted Random Forest's
    feature_importances_ would be used (we do this in evaluate.py).
    Here we use variance as a fast, model-free first pass.
    """
    feature_cols = [c for c in df.columns if c != "label"]
    numeric_df = df[feature_cols].select_dtypes(include=[np.number])
    variances = numeric_df.var()
    top_features = variances.nlargest(n_features).index.tolist()
    print(f"\n[FEATURES] Selected top {n_features} features by variance:")
    for i, f in enumerate(top_features, 1):
        print(f"  {i:2d}. {f}")
    return top_features


def preprocess(
    data_dir: Path = DATA_DIR,
    max_per_class: int = MAX_ROWS_PER_CLASS,
    n_features: int = N_FEATURES,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Full preprocessing pipeline.

    Returns a dict with:
        X_train, X_test, y_train, y_test   — numpy arrays
        feature_names                        — list of feature column names
        class_names                          — list of class label strings
        label_encoder                        — fitted LabelEncoder
        scaler                               — fitted StandardScaler
    """
    print("=" * 60)
    print("AI-SNIDS: Data Preprocessing Pipeline")
    print("=" * 60)

    # ── Step 1: Load data ──────────────────────────────────────
    df = load_cicids_files(data_dir)
    if df is None:
        # Fallback: try the synthetic dataset
        synthetic_path = data_dir / "synthetic_traffic.csv"
        if synthetic_path.exists():
            print(f"  [INFO] No CICIDS2017 files found. Using synthetic dataset: {synthetic_path}")
            df = pd.read_csv(synthetic_path)
            # Synthetic CSV already has clean column names and a 'label' column
            df = df.dropna()
            df = df[df["label"].isin(TARGET_CLASSES)]
            print(f"  [LOAD] Synthetic dataset: {len(df):,} rows")
        else:
            raise FileNotFoundError(
                "\n\n[ERROR] No CICIDS2017 CSV files found in data/\n"
                "Please download the required files as described in data/README.md\n"
                "OR run first: python ai/generate_synthetic.py\n"
            )

    # ── Step 2: Find label column ──────────────────────────────
    # Synthetic CSV uses 'label' directly; CICIDS2017 uses ' Label'
    is_synthetic = (
        "label" in df.columns
        and "Label" not in df.columns
        and " Label" not in df.columns
    )
    if is_synthetic:
        label_col = "label"
        df = df[df["label"].isin(TARGET_CLASSES)].copy()
    else:
        label_col = find_label_column(df)
    print(f"\n[INFO] Label column: '{label_col}'")

    # ── Step 3: Class distribution (raw) ──────────────────────
    print("\n[INFO] Raw class distribution:")
    raw_dist = df[label_col].astype(str).str.strip().value_counts()
    for cls, cnt in raw_dist.head(10).items():
        print(f"  {cls:<30}: {cnt:>10,}")

    # ── Step 4: Clean ──────────────────────────────────────────
    if is_synthetic:
        # Synthetic data already has clean labels — just handle numeric cleaning
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df.dropna(subset=numeric_cols, inplace=True)
        print(f"  [CLEAN] Synthetic data clean: {len(df):,} rows")
    else:
        df = clean_data(df, label_col)

    # ── Step 5: Balance ────────────────────────────────────────
    df = sample_balanced(df, max_per_class)

    # ── Step 6: Feature selection ──────────────────────────────
    # Ensure we use the unified 'label' column name
    if "label" not in df.columns and label_col in df.columns:
        df["label"] = df[label_col]

    feature_names = select_features(df, n_features)

    X = df[feature_names].values
    y = df["label"].values

    # ── Step 7: Encode labels ──────────────────────────────────
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"\n[ENCODE] Classes: {list(le.classes_)}")

    # ── Step 8: Train/test split ───────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
    )
    print(f"\n[SPLIT] Train: {len(X_train):,}  |  Test: {len(X_test):,}")

    # ── Step 9: Scale features ─────────────────────────────────
    # Why scale? Random Forest doesn't strictly need scaling, but it helps
    # with consistent feature importance magnitudes and future model comparisons.
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)   # Fit ONLY on training data
    X_test = scaler.transform(X_test)          # Transform test using training stats
    # WHY? If we fit the scaler on all data, we leak test-set statistics
    # into the training process — a form of data leakage.
    print("[SCALE] Applied StandardScaler (fit on train only)")

    # ── Step 10: Save artifacts ────────────────────────────────
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(le, MODEL_DIR / "label_encoder.pkl")
    with open(MODEL_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    print(f"\n[SAVE] Artifacts saved to {MODEL_DIR}/")
    print("  → scaler.pkl")
    print("  → label_encoder.pkl")
    print("  → feature_names.json")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_names": feature_names,
        "class_names": list(le.classes_),
        "label_encoder": le,
        "scaler": scaler,
    }


if __name__ == "__main__":
    result = preprocess()
    print(f"\n[DONE] Preprocessing complete.")
    print(f"       X_train shape: {result['X_train'].shape}")
    print(f"       Classes: {result['class_names']}")
