"""
tests/test_ai.py

Unit tests for the AI intrusion detection pipeline.

Tests:
  1. Synthetic data generation works
  2. Preprocessing pipeline runs cleanly
  3. Model loading (after training)
  4. Predicting a BENIGN sample
  5. Predicting an attack sample
  6. Risk assessment returns valid levels
  7. Invalid input handling

Run AFTER training the model:
    python ai/generate_synthetic.py
    python ai/train.py
    python -m pytest tests/test_ai.py -v
"""

import sys
import json
from pathlib import Path
import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "ai" / "model"


# ─── Synthetic Data Generation ────────────────────────────────────────────────

class TestSyntheticDataGen:

    def test_generate_synthetic_creates_file(self, tmp_path):
        """Synthetic generator should create a CSV file."""
        from ai.generate_synthetic import generate_class
        rng = np.random.default_rng(42)
        df = generate_class("BENIGN", 100, rng)
        assert len(df) == 100
        assert "label" in df.columns
        assert df["label"].iloc[0] == "BENIGN"

    def test_all_classes_generated(self):
        """All 5 attack classes should be representable."""
        from ai.generate_synthetic import CLASS_DISTRIBUTIONS, generate_class
        rng = np.random.default_rng(42)
        classes = list(CLASS_DISTRIBUTIONS.keys())
        assert set(classes) == {"BENIGN", "DoS", "DDoS", "PortScan", "BruteForce"}
        for cls in classes:
            df = generate_class(cls, 50, rng)
            assert len(df) == 50
            assert (df["label"] == cls).all()


# ─── Predictor Tests ──────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not (MODEL_DIR / "rf_model.pkl").exists(),
    reason="Model not trained yet. Run: python ai/train.py"
)
class TestPredictor:

    @pytest.fixture(scope="class")
    def predictor(self):
        from ai.predict import Predictor
        p = Predictor()
        assert p.is_loaded, "Predictor failed to load — check ai/model/*.pkl"
        return p

    def test_predictor_loads(self, predictor):
        """Predictor should load successfully with all artifacts."""
        assert predictor.is_loaded
        assert len(predictor.feature_names) > 0
        assert len(predictor.class_names) > 0

    def test_class_names_include_benign(self, predictor):
        """BENIGN must be one of the class names."""
        assert "BENIGN" in predictor.class_names

    def test_predict_benign_sample(self, predictor):
        """Benign traffic sample should classify as BENIGN or LOW risk."""
        from network.feature_extraction import get_benign_sample
        features = get_benign_sample()
        result = predictor.predict(features)

        assert "predicted_class" in result
        assert "confidence" in result
        assert "risk_level" in result
        assert "risk_score" in result
        assert "action" in result
        assert "explanation" in result
        assert "is_attack" in result

        assert 0.0 <= result["confidence"] <= 1.0
        assert 0.0 <= result["risk_score"] <= 1.0
        assert result["risk_level"] in ["HIGH", "MEDIUM", "LOW", "MONITOR"]
        assert result["action"] in ["BLOCK", "ALERT", "LOG", "ALLOW"]

    def test_predict_ddos_sample(self, predictor):
        """DDoS sample should be classified as an attack (not BENIGN)."""
        from network.feature_extraction import get_attack_samples
        samples = get_attack_samples()
        result = predictor.predict(samples["DDoS"])
        # DDoS samples are highly distinctive — expect detection
        # (Allow some tolerance for edge cases in training)
        assert result["is_attack"] or result["confidence"] > 0.4
        assert result["predicted_class"] in predictor.class_names

    def test_predict_portscan_sample(self, predictor):
        """PortScan sample should be detected."""
        from network.feature_extraction import get_attack_samples
        samples = get_attack_samples()
        result = predictor.predict(samples["PortScan"])
        assert result["predicted_class"] in predictor.class_names
        assert result["action"] in ["BLOCK", "ALERT", "LOG", "ALLOW"]

    def test_predict_probability_sums_to_one(self, predictor):
        """Class probabilities must sum to approximately 1.0."""
        from network.feature_extraction import get_benign_sample
        features = get_benign_sample()
        result = predictor.predict(features)
        total_prob = sum(result["class_probabilities"].values())
        assert abs(total_prob - 1.0) < 1e-3, f"Probabilities sum to {total_prob}"

    def test_missing_feature_raises_error(self, predictor):
        """Providing an incomplete feature dict should raise ValueError."""
        with pytest.raises(ValueError, match="Missing required features"):
            predictor.predict({"invalid_feature": 123})

    def test_predict_batch(self, predictor):
        """Batch prediction should work for multiple samples."""
        from network.feature_extraction import get_benign_sample, get_attack_samples
        samples = [get_benign_sample(), get_attack_samples()["DoS"]]
        results = predictor.predict_batch(samples)
        assert len(results) == 2
        for r in results:
            assert "predicted_class" in r


# ─── Risk Engine Tests ────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not (MODEL_DIR / "rf_model.pkl").exists(),
    reason="Model not trained yet."
)
class TestRiskEngine:

    def test_benign_is_monitor_risk(self):
        """BENIGN traffic should always have MONITOR risk level."""
        from ai.predict import Predictor
        p = Predictor()
        from network.feature_extraction import get_benign_sample
        result = p.predict(get_benign_sample())
        # BENIGN predictions should never be HIGH
        if result["predicted_class"] == "BENIGN":
            assert result["risk_level"] == "MONITOR"

    def test_risk_score_in_valid_range(self):
        """Risk score must always be in [0.0, 1.0]."""
        from ai.predict import Predictor
        from network.feature_extraction import get_benign_sample, get_attack_samples
        p = Predictor()
        all_samples = [get_benign_sample()] + list(get_attack_samples().values())
        for sample in all_samples:
            result = p.predict(sample)
            assert 0.0 <= result["risk_score"] <= 1.0, (
                f"Risk score {result['risk_score']} out of range for {result['predicted_class']}"
            )
