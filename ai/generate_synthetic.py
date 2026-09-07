"""
ai/generate_synthetic.py

Synthetic network traffic dataset generator for AI-SNIDS.

PURPOSE:
--------
When the real CICIDS2017 dataset is unavailable (no download, disk space,
etc.), this script generates statistically plausible mock network traffic
data that allows the full AI pipeline to work identically.

The synthetic data uses feature distributions inspired by published CICIDS2017
research papers (mean/std values for key flow features per attack class).

IMPORTANT: This is mock data, not real captured traffic. It is suitable for
demonstrating the AI pipeline but should not be used for production IDS.

Usage:
    python ai/generate_synthetic.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ─── Configuration ─────────────────────────────────────────────────────────────

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "synthetic_traffic.csv"
ROWS_PER_CLASS = 5000
RANDOM_SEED = 42

# ─── Feature Distributions per Class ──────────────────────────────────────────
# Each class has a dict of feature: (mean, std) tuples.
# Values are approximate, based on CICIDS2017 published statistics.
# These features are the most discriminating ones in the dataset.

CLASS_DISTRIBUTIONS = {
    "BENIGN": {
        "Flow Duration":            (5_000_000, 2_000_000),
        "Total Fwd Packets":        (10, 8),
        "Total Backward Packets":   (9, 7),
        "Total Length of Fwd Packets": (2000, 1500),
        "Total Length of Bwd Packets": (8000, 5000),
        "Fwd Packet Length Max":    (500, 300),
        "Fwd Packet Length Min":    (40, 20),
        "Fwd Packet Length Mean":   (200, 100),
        "Bwd Packet Length Max":    (900, 400),
        "Bwd Packet Length Min":    (40, 20),
        "Bwd Packet Length Mean":   (600, 300),
        "Flow Bytes/s":             (3000, 2000),
        "Flow Packets/s":           (5, 4),
        "Flow IAT Mean":            (500_000, 200_000),
        "Flow IAT Std":             (300_000, 200_000),
        "Flow IAT Max":             (1_000_000, 500_000),
        "Flow IAT Min":             (1000, 800),
        "Fwd IAT Total":            (2_000_000, 1_000_000),
        "Fwd IAT Mean":             (400_000, 200_000),
        "Bwd IAT Total":            (1_500_000, 800_000),
    },
    "DoS": {
        "Flow Duration":            (500_000, 300_000),
        "Total Fwd Packets":        (500, 200),
        "Total Backward Packets":   (2, 2),
        "Total Length of Fwd Packets": (30000, 10000),
        "Total Length of Bwd Packets": (100, 80),
        "Fwd Packet Length Max":    (65535, 5000),
        "Fwd Packet Length Min":    (40, 5),
        "Fwd Packet Length Mean":   (300, 100),
        "Bwd Packet Length Max":    (60, 40),
        "Bwd Packet Length Min":    (40, 10),
        "Bwd Packet Length Mean":   (50, 20),
        "Flow Bytes/s":             (500_000, 200_000),
        "Flow Packets/s":           (5000, 2000),
        "Flow IAT Mean":            (200, 100),
        "Flow IAT Std":             (500, 300),
        "Flow IAT Max":             (10000, 5000),
        "Flow IAT Min":             (50, 30),
        "Fwd IAT Total":            (400_000, 200_000),
        "Fwd IAT Mean":             (800, 400),
        "Bwd IAT Total":            (5000, 3000),
    },
    "DDoS": {
        "Flow Duration":            (100_000, 50_000),
        "Total Fwd Packets":        (1000, 500),
        "Total Backward Packets":   (1, 1),
        "Total Length of Fwd Packets": (60000, 20000),
        "Total Length of Bwd Packets": (40, 10),
        "Fwd Packet Length Max":    (1500, 200),
        "Fwd Packet Length Min":    (1500, 50),
        "Fwd Packet Length Mean":   (1500, 100),
        "Bwd Packet Length Max":    (40, 10),
        "Bwd Packet Length Min":    (40, 5),
        "Bwd Packet Length Mean":   (40, 5),
        "Flow Bytes/s":             (1_500_000, 500_000),
        "Flow Packets/s":           (50_000, 20_000),
        "Flow IAT Mean":            (20, 10),
        "Flow IAT Std":             (50, 30),
        "Flow IAT Max":             (1000, 500),
        "Flow IAT Min":             (10, 5),
        "Fwd IAT Total":            (80_000, 40_000),
        "Fwd IAT Mean":             (80, 40),
        "Bwd IAT Total":            (0, 0),
    },
    "PortScan": {
        "Flow Duration":            (1000, 500),
        "Total Fwd Packets":        (2, 1),
        "Total Backward Packets":   (0, 0),
        "Total Length of Fwd Packets": (80, 20),
        "Total Length of Bwd Packets": (0, 0),
        "Fwd Packet Length Max":    (40, 10),
        "Fwd Packet Length Min":    (40, 5),
        "Fwd Packet Length Mean":   (40, 5),
        "Bwd Packet Length Max":    (0, 0),
        "Bwd Packet Length Min":    (0, 0),
        "Bwd Packet Length Mean":   (0, 0),
        "Flow Bytes/s":             (80_000, 40_000),
        "Flow Packets/s":           (2000, 1000),
        "Flow IAT Mean":            (500, 300),
        "Flow IAT Std":             (100, 50),
        "Flow IAT Max":             (1000, 500),
        "Flow IAT Min":             (50, 30),
        "Fwd IAT Total":            (500, 300),
        "Fwd IAT Mean":             (250, 100),
        "Bwd IAT Total":            (0, 0),
    },
    "BruteForce": {
        "Flow Duration":            (2_000_000, 1_000_000),
        "Total Fwd Packets":        (20, 10),
        "Total Backward Packets":   (15, 8),
        "Total Length of Fwd Packets": (1000, 500),
        "Total Length of Bwd Packets": (2000, 1000),
        "Fwd Packet Length Max":    (200, 100),
        "Fwd Packet Length Min":    (40, 10),
        "Fwd Packet Length Mean":   (80, 40),
        "Bwd Packet Length Max":    (400, 200),
        "Bwd Packet Length Min":    (40, 20),
        "Bwd Packet Length Mean":   (150, 80),
        "Flow Bytes/s":             (1500, 800),
        "Flow Packets/s":           (18, 10),
        "Flow IAT Mean":            (100_000, 50_000),
        "Flow IAT Std":             (80_000, 40_000),
        "Flow IAT Max":             (500_000, 200_000),
        "Flow IAT Min":             (500, 300),
        "Fwd IAT Total":            (1_000_000, 500_000),
        "Fwd IAT Mean":             (100_000, 50_000),
        "Bwd IAT Total":            (800_000, 400_000),
    },
}


def generate_class(class_name: str, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate n rows of synthetic traffic for a given attack class."""
    dist = CLASS_DISTRIBUTIONS[class_name]
    data = {}
    for feature, (mean, std) in dist.items():
        if std == 0:
            data[feature] = np.zeros(n)
        else:
            # Normal distribution, clipped at 0 (no negative packet lengths etc.)
            data[feature] = np.clip(rng.normal(mean, std, n), 0, None)
    df = pd.DataFrame(data)
    df["label"] = class_name
    return df


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    print("[SYNTH] Generating synthetic CICIDS2017-like dataset...")

    frames = []
    for cls_name, n in zip(CLASS_DISTRIBUTIONS.keys(), [ROWS_PER_CLASS] * 5):
        df = generate_class(cls_name, n, rng)
        frames.append(df)
        print(f"  {cls_name:<15}: {n:,} rows generated")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False)

    print(f"\n[SYNTH] Saved {len(combined):,} rows to: {OUTPUT_PATH}")
    print(f"[SYNTH] Columns: {list(combined.columns)}")

    # Save feature list for the preprocessor to discover
    features = [c for c in combined.columns if c != "label"]
    feature_path = OUTPUT_PATH.parent / "synthetic_feature_names.json"
    with open(feature_path, "w") as f:
        json.dump(features, f, indent=2)
    print(f"[SYNTH] Feature list saved to: {feature_path}")


if __name__ == "__main__":
    main()
