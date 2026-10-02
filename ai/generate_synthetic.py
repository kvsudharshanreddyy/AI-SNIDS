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
        "Fwd IAT Total":     (4.0, 1.0),
        "Flow Duration":     (148_470.0, 30_000.0),
        "Idle Max":          (0.0, 0.0),
        "Fwd IAT Max":       (4.0, 1.0),
        "Flow IAT Max":      (105_606.0, 20_000.0),
        "Idle Mean":         (0.0, 0.0),
        "Idle Min":          (0.0, 0.0),
        "Bwd IAT Total":     (48.5, 10.0),
        "Bwd IAT Max":       (48.0, 10.0),
        "Flow Bytes/s":      (2_504.6, 500.0),
        "Fwd IAT Std":       (0.0, 0.0),
        "Flow IAT Std":      (28_887.0, 5_000.0),
        "Fwd IAT Mean":      (4.0, 1.0),
        "Bwd IAT Std":       (0.0, 0.0),
        "Fwd Header Length": (60.0, 10.0),
        "Fwd Header Length.1": (60.0, 10.0),
        "Idle Std":          (0.0, 0.0),
        "Bwd IAT Mean":      (48.0, 10.0),
        "Fwd IAT Min":       (3.0, 0.5),
        "Bwd IAT Min":       (3.0, 0.5),
    },
    "DoS": {
        "Fwd IAT Total":     (84_800_000.0, 5_000_000.0),
        "Flow Duration":     (84_908_153.0, 5_000_000.0),
        "Idle Max":          (84_600_000.0, 5_000_000.0),
        "Fwd IAT Max":       (84_600_000.0, 5_000_000.0),
        "Flow IAT Max":      (84_600_000.0, 5_000_000.0),
        "Idle Mean":         (84_500_000.0, 5_000_000.0),
        "Idle Min":          (84_500_000.0, 5_000_000.0),
        "Bwd IAT Total":     (83_100.0, 10_000.0),
        "Bwd IAT Max":       (71_249.0, 10_000.0),
        "Flow Bytes/s":      (121.7, 20.0),
        "Fwd IAT Std":       (33_850_000.0, 2_000_000.0),
        "Flow IAT Std":      (23_700_000.0, 2_000_000.0),
        "Fwd IAT Mean":      (12_450_000.0, 1_000_000.0),
        "Bwd IAT Std":       (29_848.0, 5_000.0),
        "Fwd Header Length": (164.0, 20.0),
        "Fwd Header Length.1": (164.0, 20.0),
        "Idle Std":          (0.0, 0.0),
        "Bwd IAT Mean":      (17_126.0, 2_000.0),
        "Fwd IAT Min":       (3.0, 0.5),
        "Bwd IAT Min":       (45.0, 5.0),
    },
    "DDoS": {
        "Fwd IAT Total":     (747.0, 100.0),
        "Flow Duration":     (1_293_792.0, 100_000.0),
        "Idle Max":          (0.0, 0.0),
        "Fwd IAT Max":       (744.0, 100.0),
        "Flow IAT Max":      (1_292_730.0, 100_000.0),
        "Idle Mean":         (0.0, 0.0),
        "Idle Min":          (0.0, 0.0),
        "Bwd IAT Total":     (1_293_746.0, 100_000.0),
        "Bwd IAT Max":       (1_292_730.0, 100_000.0),
        "Flow Bytes/s":      (8_991.4, 1_000.0),
        "Fwd IAT Std":       (523.9, 50.0),
        "Flow IAT Std":      (430_865.0, 50_000.0),
        "Fwd IAT Mean":      (373.5, 50.0),
        "Bwd IAT Std":       (527_671.0, 50_000.0),
        "Fwd Header Length": (72.0, 10.0),
        "Fwd Header Length.1": (72.0, 10.0),
        "Idle Std":          (0.0, 0.0),
        "Bwd IAT Mean":      (215_624.0, 30_000.0),
        "Fwd IAT Min":       (3.0, 0.5),
        "Bwd IAT Min":       (2.0, 0.5),
    },
    "PortScan": {
        "Fwd IAT Total":     (0.0, 0.0),
        "Flow Duration":     (48.0, 5.0),
        "Idle Max":          (0.0, 0.0),
        "Fwd IAT Max":       (0.0, 0.0),
        "Flow IAT Max":      (48.0, 5.0),
        "Idle Mean":         (0.0, 0.0),
        "Idle Min":          (0.0, 0.0),
        "Bwd IAT Total":     (0.0, 0.0),
        "Bwd IAT Max":       (0.0, 0.0),
        "Flow Bytes/s":      (139_534.0, 15_000.0),
        "Fwd IAT Std":       (0.0, 0.0),
        "Flow IAT Std":      (0.0, 0.0),
        "Fwd IAT Mean":      (0.0, 0.0),
        "Bwd IAT Std":       (0.0, 0.0),
        "Fwd Header Length": (24.0, 4.0),
        "Fwd Header Length.1": (24.0, 4.0),
        "Idle Std":          (0.0, 0.0),
        "Bwd IAT Mean":      (0.0, 0.0),
        "Fwd IAT Min":       (0.0, 0.0),
        "Bwd IAT Min":       (0.0, 0.0),
    },
    "BruteForce": {
        "Fwd IAT Total":     (5_316_565.0, 500_000.0),
        "Flow Duration":     (8_210_721.0, 500_000.0),
        "Idle Max":          (0.0, 0.0),
        "Fwd IAT Max":       (2_792_138.0, 300_000.0),
        "Flow IAT Max":      (2_910_882.0, 300_000.0),
        "Idle Mean":         (0.0, 0.0),
        "Idle Min":          (0.0, 0.0),
        "Bwd IAT Total":     (8_210_631.0, 500_000.0),
        "Bwd IAT Max":       (2_910_882.0, 300_000.0),
        "Flow Bytes/s":      (35.8, 5.0),
        "Fwd IAT Std":       (1_225_393.0, 100_000.0),
        "Flow IAT Std":      (927_880.0, 100_000.0),
        "Fwd IAT Mean":      (665_530.0, 50_000.0),
        "Bwd IAT Std":       (1_147_637.0, 100_000.0),
        "Fwd Header Length": (296.0, 30.0),
        "Fwd Header Length.1": (296.0, 30.0),
        "Idle Std":          (0.0, 0.0),
        "Bwd IAT Mean":      (589_812.0, 50_000.0),
        "Fwd IAT Min":       (50.5, 5.0),
        "Bwd IAT Min":       (1.5, 0.5),
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
