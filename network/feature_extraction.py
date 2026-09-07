"""
network/feature_extraction.py

Network traffic feature extraction for AI-SNIDS.

This module provides:
1. A function to extract features from Scapy packets (live capture)
2. A function to map a CSV row (CICIDS2017 format) to our feature format
3. Sample traffic generators for demonstration

WHY SCAPY?
----------
Scapy is a pure-Python packet manipulation/capture library. Unlike
Wireshark or tcpdump (compiled C binaries), Scapy gives us programmatic
access to packet fields at the Python level — making it easy to integrate
with our ML pipeline.

IMPORTANT CONSTRAINTS:
----------------------
Live packet capture requires elevated privileges (root/sudo on Linux).
For the academic prototype:
- CICIDS2017 CSV files are the PRIMARY data source (no privilege needed)
- Live capture is an OPTIONAL feature
"""

import json
import time
from pathlib import Path
from typing import Optional

# ─── Dynamic feature loading ───────────────────────────────────────────────────
# Load feature names from the trained model to guarantee alignment.
# Falls back to a static list if the model has not been trained yet.

_MODEL_DIR = Path(__file__).parent.parent / "ai" / "model"
_FEATURE_NAMES_PATH = _MODEL_DIR / "feature_names.json"

# Real CICIDS2017 trained feature set (top-20 by variance).
# This MUST match ai/model/feature_names.json after training.
_DEFAULT_FEATURES = [
    "Fwd IAT Total",
    "Flow Duration",
    "Idle Max",
    "Fwd IAT Max",
    "Flow IAT Max",
    "Idle Mean",
    "Idle Min",
    "Bwd IAT Total",
    "Bwd IAT Max",
    "Flow Bytes/s",
    "Fwd IAT Std",
    "Flow IAT Std",
    "Fwd IAT Mean",
    "Bwd IAT Std",
    "Fwd Header Length",
    "Fwd Header Length.1",
    "Idle Std",
    "Bwd IAT Mean",
    "Fwd IAT Min",
    "Bwd IAT Min",
]


def get_feature_names() -> list[str]:
    """
    Return the feature names expected by the trained model.
    Reads from ai/model/feature_names.json if available, otherwise
    returns the default real-CICIDS2017 feature set.
    """
    if _FEATURE_NAMES_PATH.exists():
        with open(_FEATURE_NAMES_PATH) as f:
            return json.load(f)
    return _DEFAULT_FEATURES


# Module-level constant — loaded once at import
FEATURE_NAMES = get_feature_names()


def extract_features_from_csv_row(row: dict) -> dict:
    """
    Extract model-ready features from a CICIDS2017 CSV row (as dict).

    Args:
        row: dict with keys matching CICIDS2017 column names

    Returns:
        dict with feature_name → float value
    """
    import numpy as np
    features = {}

    for feature in FEATURE_NAMES:
        val = row.get(feature, row.get(f" {feature}", 0.0))
        try:
            val = float(val)
            if not np.isfinite(val):
                val = 0.0
        except (ValueError, TypeError):
            val = 0.0
        features[feature] = val

    return features


def extract_features_from_packets(packets: list) -> Optional[dict]:
    """
    Extract flow features from a list of Scapy packets.

    Args:
        packets: List of Scapy packet objects (from sniff() or rdpcap())

    Returns:
        dict of feature_name → float, or None if no valid packets
    """
    try:
        from scapy.layers.inet import IP, TCP, UDP
        import numpy as np
    except ImportError:
        print("[NETWORK] Scapy not available — cannot extract live features")
        return None

    if not packets:
        return None

    fwd_lengths = []
    bwd_lengths = []
    timestamps = []

    for pkt in packets:
        if IP not in pkt:
            continue
        ts = float(pkt.time)
        pkt_len = len(pkt)
        timestamps.append(ts)

        if len(fwd_lengths) <= len(bwd_lengths):
            fwd_lengths.append(pkt_len)
        else:
            bwd_lengths.append(pkt_len)

    if not timestamps:
        return None

    n_fwd = len(fwd_lengths)
    n_bwd = len(bwd_lengths)
    flow_duration = max((timestamps[-1] - timestamps[0]) * 1_000_000, 1)

    iats = [
        (timestamps[i+1] - timestamps[i]) * 1_000_000
        for i in range(len(timestamps) - 1)
    ] or [0]

    iat_arr = np.array(iats)
    total_bytes = sum(fwd_lengths) + sum(bwd_lengths)
    flow_bytes_per_s = total_bytes / (flow_duration / 1_000_000) if flow_duration > 0 else 0
    fwd_hdr = n_fwd * 20

    return {
        "Fwd IAT Total":     float(iat_arr.sum()),
        "Flow Duration":     flow_duration,
        "Idle Max":          0.0,
        "Fwd IAT Max":       float(iat_arr.max()),
        "Flow IAT Max":      float(iat_arr.max()),
        "Idle Mean":         0.0,
        "Idle Min":          0.0,
        "Bwd IAT Total":     float(iat_arr.sum()) if n_bwd > 0 else 0.0,
        "Bwd IAT Max":       float(iat_arr.max()) if n_bwd > 0 else 0.0,
        "Flow Bytes/s":      flow_bytes_per_s,
        "Fwd IAT Std":       float(iat_arr.std()),
        "Flow IAT Std":      float(iat_arr.std()),
        "Fwd IAT Mean":      float(iat_arr.mean()),
        "Bwd IAT Std":       float(iat_arr.std()) if n_bwd > 0 else 0.0,
        "Fwd Header Length": float(fwd_hdr),
        "Fwd Header Length.1": float(fwd_hdr),
        "Idle Std":          0.0,
        "Bwd IAT Mean":      float(iat_arr.mean()) if n_bwd > 0 else 0.0,
        "Fwd IAT Min":       float(iat_arr.min()),
        "Bwd IAT Min":       float(iat_arr.min()) if n_bwd > 0 else 0.0,
    }


def _make_sample(overrides: dict) -> dict:
    """
    Build a sample feature dict with safe defaults for all model features,
    then apply overrides for the specific traffic type.
    Guarantees ALL required model features are always present.
    """
    base = {
        "Fwd IAT Total":     0.0,
        "Flow Duration":     1_000_000.0,
        "Idle Max":          0.0,
        "Fwd IAT Max":       0.0,
        "Flow IAT Max":      0.0,
        "Idle Mean":         0.0,
        "Idle Min":          0.0,
        "Bwd IAT Total":     0.0,
        "Bwd IAT Max":       0.0,
        "Flow Bytes/s":      1000.0,
        "Fwd IAT Std":       0.0,
        "Flow IAT Std":      0.0,
        "Fwd IAT Mean":      0.0,
        "Bwd IAT Std":       0.0,
        "Fwd Header Length": 200.0,
        "Fwd Header Length.1": 200.0,
        "Idle Std":          0.0,
        "Bwd IAT Mean":      0.0,
        "Fwd IAT Min":       0.0,
        "Bwd IAT Min":       0.0,
    }
    base.update(overrides)
    return base


def get_benign_sample() -> dict:
    """Return a sample feature dict typical of benign web browsing traffic.
    Values are real medians from CICIDS2017 Friday-DDos file BENIGN rows.
    """
    return _make_sample({
        "Fwd IAT Total":     4.0,
        "Flow Duration":     148_470.0,
        "Idle Max":          0.0,
        "Fwd IAT Max":       4.0,
        "Flow IAT Max":      105_606.0,
        "Idle Mean":         0.0,
        "Idle Min":          0.0,
        "Bwd IAT Total":     48.5,
        "Bwd IAT Max":       48.0,
        "Flow Bytes/s":      2_504.6,
        "Fwd IAT Std":       0.0,
        "Flow IAT Std":      28_887.0,
        "Fwd IAT Mean":      4.0,
        "Bwd IAT Std":       0.0,
        "Fwd Header Length": 60.0,
        "Fwd Header Length.1": 60.0,
        "Idle Std":          0.0,
        "Bwd IAT Mean":      48.0,
        "Fwd IAT Min":       3.0,
        "Bwd IAT Min":       3.0,
    })


def get_attack_samples() -> dict[str, dict]:
    """
    Return sample feature dicts for each attack class.
    Values are real medians from the CICIDS2017 dataset — the same data
    the model was trained on — so predictions should be accurate.
    """
    return {
        "DoS": _make_sample({
            # DoS Hulk real medians (Wednesday-workingHours.pcap_ISCX.csv)
            # Key signal: enormous Idle Max/Mean/Min (flow pauses between sends)
            "Fwd IAT Total":     84_800_000.0,
            "Flow Duration":     84_908_153.0,
            "Idle Max":          84_600_000.0,   # ← primary DoS discriminator
            "Fwd IAT Max":       84_600_000.0,
            "Flow IAT Max":      84_600_000.0,
            "Idle Mean":         84_500_000.0,
            "Idle Min":          84_500_000.0,
            "Bwd IAT Total":     83_100.0,
            "Bwd IAT Max":       71_249.0,
            "Flow Bytes/s":      121.7,
            "Fwd IAT Std":       33_850_000.0,
            "Flow IAT Std":      23_700_000.0,
            "Fwd IAT Mean":      12_450_000.0,
            "Bwd IAT Std":       29_848.0,
            "Fwd Header Length": 164.0,
            "Fwd Header Length.1": 164.0,
            "Idle Std":          0.0,
            "Bwd IAT Mean":      17_126.0,
            "Fwd IAT Min":       3.0,
            "Bwd IAT Min":       45.0,
        }),

        "DDoS": _make_sample({
            # Real CICIDS2017 DDoS row (Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv)
            # Key discriminator: large Fwd IAT Total + large Flow IAT Std vs BENIGN
            "Fwd IAT Total":     747.0,
            "Flow Duration":     1_293_792.0,
            "Idle Max":          0.0,
            "Fwd IAT Max":       744.0,
            "Flow IAT Max":      1_292_730.0,
            "Idle Mean":         0.0,
            "Idle Min":          0.0,
            "Bwd IAT Total":     1_293_746.0,
            "Bwd IAT Max":       1_292_730.0,
            "Flow Bytes/s":      8_991.4,
            "Fwd IAT Std":       523.9,
            "Flow IAT Std":      430_865.0,
            "Fwd IAT Mean":      373.5,
            "Bwd IAT Std":       527_671.0,
            "Fwd Header Length": 72.0,
            "Fwd Header Length.1": 72.0,
            "Idle Std":          0.0,
            "Bwd IAT Mean":      215_624.0,
            "Fwd IAT Min":       3.0,
            "Bwd IAT Min":       2.0,
        }),

        "PortScan": _make_sample({
            # PortScan real medians (Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv)
            # Key signal: very short duration, zero IATs, high bytes/s, tiny header length
            "Fwd IAT Total":     0.0,
            "Flow Duration":     48.0,
            "Idle Max":          0.0,
            "Fwd IAT Max":       0.0,
            "Flow IAT Max":      48.0,
            "Idle Mean":         0.0,
            "Idle Min":          0.0,
            "Bwd IAT Total":     0.0,
            "Bwd IAT Max":       0.0,
            "Flow Bytes/s":      139_534.0,
            "Fwd IAT Std":       0.0,
            "Flow IAT Std":      0.0,
            "Fwd IAT Mean":      0.0,
            "Bwd IAT Std":       0.0,
            "Fwd Header Length": 24.0,
            "Fwd Header Length.1": 24.0,
            "Idle Std":          0.0,
            "Bwd IAT Mean":      0.0,
            "Fwd IAT Min":       0.0,
            "Bwd IAT Min":       0.0,
        }),

        "BruteForce": _make_sample({
            # FTP-Patator real medians (Tuesday-WorkingHours.pcap_ISCX.csv)
            # Key signal: very long flow, high Fwd IAT Total, large Fwd Header Length
            "Fwd IAT Total":     5_316_565.0,
            "Flow Duration":     8_210_721.0,
            "Idle Max":          0.0,
            "Fwd IAT Max":       2_792_138.0,
            "Flow IAT Max":      2_910_882.0,
            "Idle Mean":         0.0,
            "Idle Min":          0.0,
            "Bwd IAT Total":     8_210_631.0,
            "Bwd IAT Max":       2_910_882.0,
            "Flow Bytes/s":      35.8,
            "Fwd IAT Std":       1_225_393.0,
            "Flow IAT Std":      927_880.0,
            "Fwd IAT Mean":      665_530.0,
            "Bwd IAT Std":       1_147_637.0,
            "Fwd Header Length": 296.0,
            "Fwd Header Length.1": 296.0,
            "Idle Std":          0.0,
            "Bwd IAT Mean":      589_812.0,
            "Fwd IAT Min":       50.5,
            "Bwd IAT Min":       1.5,
        }),
    }
