"""
ai/predict.py

AI inference pipeline for AI-SNIDS.

This module provides the Predictor class — a stateful wrapper around
the trained Random Forest model that:

1. Loads the model, scaler, and feature names from disk
2. Validates and preprocesses input feature vectors
3. Returns prediction with class probabilities
4. Feeds results into the Risk Assessment Engine

Design decision — why a class (not just a function)?
-----------------------------------------------------
Loading the model from disk is slow (~0.5s). Using a class with lazy
initialization means we load once at startup and reuse across all
prediction requests. A bare function would reload on every call.

Thread safety: sklearn's predict() is read-only and thread-safe.
"""

import json
from pathlib import Path
from typing import Optional
import sys

import joblib
import numpy as np

# ─── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "ai" / "model"

# ─── Risk Engine ───────────────────────────────────────────────────────────────

# Attack severity weights used by the risk engine.
# BENIGN has no risk. More destructive attacks get higher base weights.
ATTACK_SEVERITY = {
    "BENIGN":     0.0,
    "BruteForce": 0.5,
    "PortScan":   0.4,
    "DoS":        0.7,
    "DDoS":       0.8,
    "Botnet":     0.9,
}

# Thresholds for risk levels based on composite risk score
RISK_THRESHOLDS = {
    "HIGH":   0.70,
    "MEDIUM": 0.45,
    "LOW":    0.20,
}

# Action mapping per risk level
RISK_ACTIONS = {
    "HIGH":    "BLOCK",
    "MEDIUM":  "ALERT",
    "LOW":     "LOG",
    "MONITOR": "ALLOW",
}


class Predictor:
    """
    Wraps the trained Random Forest model for inference.

    Attributes:
        model:          Trained RandomForestClassifier
        scaler:         Fitted StandardScaler
        label_encoder:  Fitted LabelEncoder
        feature_names:  Ordered list of expected feature names
        is_loaded:      Whether the model has been loaded successfully
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names: list[str] = []
        self.is_loaded = False
        self._load()

    def _load(self) -> None:
        """Load model artifacts from disk."""
        required = {
            "model":    MODEL_DIR / "rf_model.pkl",
            "scaler":   MODEL_DIR / "scaler.pkl",
            "encoder":  MODEL_DIR / "label_encoder.pkl",
            "features": MODEL_DIR / "feature_names.json",
        }

        missing = [name for name, path in required.items() if not path.exists()]
        if missing:
            print(
                f"[PREDICTOR] Warning: Missing artifacts: {missing}\n"
                f"            Run 'python ai/train.py' to generate them."
            )
            return

        self.model = joblib.load(required["model"])
        self.scaler = joblib.load(required["scaler"])
        self.label_encoder = joblib.load(required["encoder"])
        with open(required["features"]) as f:
            self.feature_names = json.load(f)

        self.is_loaded = True
        print(f"[PREDICTOR] Model loaded: {len(self.feature_names)} features, "
              f"{len(self.label_encoder.classes_)} classes")

    def predict(self, features: dict) -> dict:
        """
        Run inference on a single traffic sample.

        Args:
            features: dict mapping feature names to float values.
                      Keys must include all features in self.feature_names.
                      Extra keys are silently ignored.

        Returns:
            dict with:
                predicted_class     (str)  — e.g., "DDoS"
                confidence          (float) — model's max class probability
                class_probabilities (dict)  — probability per class
                risk_level          (str)   — HIGH / MEDIUM / LOW / MONITOR
                risk_score          (float) — composite [0.0–1.0]
                action              (str)   — BLOCK / ALERT / LOG / ALLOW
                explanation         (str)   — human-readable rationale
                is_attack           (bool)

        Raises:
            RuntimeError: if model is not loaded
            ValueError:   if required features are missing
        """
        if not self.is_loaded:
            raise RuntimeError(
                "Model not loaded. Run 'python ai/train.py' first."
            )

        # ── Build feature vector ────────────────────────────────
        x_raw = self._build_feature_vector(features)

        # ── Scale ───────────────────────────────────────────────
        x_scaled = self.scaler.transform(x_raw.reshape(1, -1))

        # ── Predict ─────────────────────────────────────────────
        y_pred_encoded = self.model.predict(x_scaled)[0]
        y_proba = self.model.predict_proba(x_scaled)[0]

        predicted_class = self.label_encoder.inverse_transform([y_pred_encoded])[0]
        confidence = float(np.max(y_proba))

        class_probabilities = {
            cls: float(prob)
            for cls, prob in zip(self.label_encoder.classes_, y_proba)
        }

        # ── Risk Assessment ─────────────────────────────────────
        risk_score, risk_level, action = self._assess_risk(
            predicted_class, confidence, features
        )

        # ── Explanation ─────────────────────────────────────────
        explanation = self._explain(
            predicted_class, confidence, risk_level, class_probabilities
        )

        return {
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "class_probabilities": {k: round(v, 4) for k, v in class_probabilities.items()},
            "risk_level": risk_level,
            "risk_score": round(risk_score, 4),
            "action": action,
            "explanation": explanation,
            "is_attack": predicted_class != "BENIGN",
        }

    def predict_batch(self, feature_dicts: list[dict]) -> list[dict]:
        """Run inference on multiple samples. Returns list of predict() results."""
        return [self.predict(f) for f in feature_dicts]

    def _build_feature_vector(self, features: dict) -> np.ndarray:
        """Convert input dict to ordered numpy array matching trained feature order."""
        missing = [f for f in self.feature_names if f not in features]
        if missing:
            raise ValueError(
                f"Missing required features: {missing[:5]}{'...' if len(missing) > 5 else ''}\n"
                f"Required: {self.feature_names}"
            )
        return np.array([float(features[f]) for f in self.feature_names])

    def _assess_risk(
        self,
        predicted_class: str,
        confidence: float,
        raw_features: dict,
    ) -> tuple[float, str, str]:
        """
        Calculate a composite risk score.

        Components:
        1. Model confidence (40% weight)
        2. Attack severity weight (40% weight)
        3. Traffic intensity bonus (20% weight)

        WHY a composite score?
        ----------------------
        Raw model probability is not the same as real-world risk.
        A PortScan with 95% confidence is less dangerous than a DDoS
        with 70% confidence. The composite score blends model certainty
        with the inherent severity of each attack type.

        The result is still labeled "Model-derived Risk" to make clear
        it is not the same as a real threat intelligence score.
        """
        severity = ATTACK_SEVERITY.get(predicted_class, 0.3)

        # Intensity signal from packet rate (if available)
        pkt_rate = float(raw_features.get("Flow Packets/s", 0))
        intensity = min(pkt_rate / 100_000, 1.0)   # Normalize to [0, 1]

        # Composite weighted score
        risk_score = (0.4 * confidence) + (0.4 * severity) + (0.2 * intensity)
        risk_score = float(np.clip(risk_score, 0.0, 1.0))

        # Map score to level
        if predicted_class == "BENIGN":
            risk_level = "MONITOR"
        elif risk_score >= RISK_THRESHOLDS["HIGH"]:
            risk_level = "HIGH"
        elif risk_score >= RISK_THRESHOLDS["MEDIUM"]:
            risk_level = "MEDIUM"
        elif risk_score >= RISK_THRESHOLDS["LOW"]:
            risk_level = "LOW"
        else:
            risk_level = "MONITOR"

        action = RISK_ACTIONS[risk_level]
        return risk_score, risk_level, action

    def _explain(
        self,
        predicted_class: str,
        confidence: float,
        risk_level: str,
        probabilities: dict,
    ) -> str:
        """
        Generate a human-readable explanation of the prediction.

        Why explainability matters in IDS:
        - Security analysts need to understand WHY traffic was flagged
        - Blind "black box" alerts are ignored or overridden
        - Explainability builds trust and aids in incident response
        """
        if predicted_class == "BENIGN":
            return (
                f"Traffic classified as BENIGN with {confidence * 100:.1f}% confidence. "
                f"Flow characteristics match normal network behavior patterns."
            )

        # Build a sorted probability summary for top-2 alternatives
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        top2 = sorted_probs[:2]

        explanations = {
            "DoS": (
                "High packet rate with minimal response traffic detected. "
                "DoS attacks attempt to exhaust target resources by flooding "
                "with requests, causing legitimate service disruption."
            ),
            "DDoS": (
                "Extremely high packet rate from potentially distributed sources. "
                "DDoS amplifies DoS impact using multiple attacking nodes, "
                "making mitigation significantly harder."
            ),
            "PortScan": (
                "Short-lived flows to many ports detected. "
                "Port scanning is a reconnaissance technique used to identify "
                "open services before launching targeted attacks."
            ),
            "BruteForce": (
                "Repeated authentication attempts with small data payloads. "
                "Brute force attacks systematically try credentials, targeting "
                "services like SSH, FTP, or web login forms."
            ),
            "Botnet": (
                "Traffic pattern consistent with C2 (command-and-control) communication. "
                "Botnet traffic often features periodic, low-volume beaconing behavior."
            ),
        }

        base_explanation = explanations.get(
            predicted_class,
            f"Anomalous traffic pattern detected matching {predicted_class} signatures."
        )

        # Safe: only show second entry if it exists
        if len(top2) >= 2:
            alt_str = (
                f"(Top predictions: {top2[0][0]}={top2[0][1] * 100:.1f}%, "
                f"{top2[1][0]}={top2[1][1] * 100:.1f}%)"
            )
        else:
            alt_str = f"(Predicted: {top2[0][0]}={top2[0][1] * 100:.1f}%)"

        return (
            f"ALERT: {predicted_class} traffic detected with {confidence * 100:.1f}% model confidence. "
            f"Risk level: {risk_level}. "
            f"{base_explanation} "
            f"{alt_str}"
        )

    @property
    def class_names(self) -> list[str]:
        """Return list of class names in encoded order."""
        if self.label_encoder:
            return list(self.label_encoder.classes_)
        return []


# ─── Singleton instance ────────────────────────────────────────────────────────
# Created once at module import; reused across all callers
_predictor_instance: Optional[Predictor] = None


def get_predictor() -> Predictor:
    """Return the singleton Predictor instance (lazy initialization)."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = Predictor()
    return _predictor_instance


def predict_single(features: dict) -> dict:
    """Convenience function — runs a single prediction using the singleton."""
    return get_predictor().predict(features)
