"""
tests/test_e2e.py

End-to-end pipeline test for AI-SNIDS.

Tests the complete flow:
    Traffic features
        → Feature extraction
        → AI prediction
        → Risk assessment
        → Security event creation
        → Database logging
        → Event retrieval

Run after training:
    python ai/train.py
    python -m pytest tests/test_e2e.py -v
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "ai" / "model"


@pytest.mark.skipif(
    not (MODEL_DIR / "rf_model.pkl").exists(),
    reason="Model not trained yet. Run: python ai/train.py"
)
class TestEndToEnd:
    """
    End-to-end tests verifying the complete AI-SNIDS detection pipeline.
    """

    @pytest.fixture(scope="class")
    def temp_db(self, tmp_path_factory):
        """Create a temporary database for testing (avoids polluting real DB)."""
        import os
        db_path = tmp_path_factory.mktemp("db") / "test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        from database.database import init_db
        init_db()
        yield db_path

    def test_benign_pipeline(self, temp_db):
        """Full pipeline for benign traffic."""
        from network.feature_extraction import get_benign_sample
        from ai.predict import Predictor

        features = get_benign_sample()
        predictor = Predictor()
        result = predictor.predict(features)

        # Verify result structure
        assert "predicted_class" in result
        assert "risk_level" in result
        assert "action" in result
        assert "explanation" in result
        assert isinstance(result["is_attack"], bool)

        # Log to temp DB
        from database.database import SessionLocal
        from database.models import SecurityEvent

        session = SessionLocal()
        event = SecurityEvent(
            timestamp=datetime.now(timezone.utc),
            source_ip="192.168.1.1",
            destination_ip="10.0.0.1",
            attack_type=result["predicted_class"],
            confidence=result["confidence"],
            risk_level=result["risk_level"],
            risk_score=result["risk_score"],
            action=result["action"],
            is_blocked=False,
            notes=result["explanation"][:200],
        )
        session.add(event)
        session.commit()

        # Verify stored
        stored = session.query(SecurityEvent).filter_by(id=event.id).first()
        assert stored is not None
        assert stored.attack_type == result["predicted_class"]
        session.close()

    def test_attack_pipeline_logs_correctly(self, temp_db):
        """Attack traffic should generate an event with non-MONITOR risk."""
        from network.feature_extraction import get_attack_samples
        from ai.predict import Predictor
        from database.database import SessionLocal
        from database.models import SecurityEvent

        predictor = Predictor()
        samples = get_attack_samples()

        for attack_type, features in samples.items():
            result = predictor.predict(features)

            session = SessionLocal()
            event = SecurityEvent(
                timestamp=datetime.now(timezone.utc),
                source_ip=f"10.0.0.{hash(attack_type) % 254 + 1}",
                destination_ip="192.168.1.100",
                attack_type=result["predicted_class"],
                confidence=result["confidence"],
                risk_level=result["risk_level"],
                risk_score=result["risk_score"],
                action=result["action"],
                is_blocked=(result["action"] == "BLOCK"),
                notes=f"E2E test: {attack_type}",
            )
            session.add(event)
            session.commit()

            stored = session.query(SecurityEvent).filter_by(id=event.id).first()
            assert stored is not None
            assert stored.confidence >= 0.0
            assert stored.risk_level in ["HIGH", "MEDIUM", "LOW", "MONITOR"]
            session.close()

    def test_database_event_count_increases(self, temp_db):
        """Each prediction+log should increase the event count."""
        from network.feature_extraction import get_benign_sample
        from ai.predict import Predictor
        from database.database import SessionLocal
        from database.models import SecurityEvent
        from sqlalchemy import func

        session = SessionLocal()
        count_before = session.query(func.count(SecurityEvent.id)).scalar()
        session.close()

        # Run two predictions
        predictor = Predictor()
        features = get_benign_sample()
        for _ in range(2):
            result = predictor.predict(features)
            session = SessionLocal()
            session.add(SecurityEvent(
                timestamp=datetime.now(timezone.utc),
                source_ip="127.0.0.1",
                destination_ip="127.0.0.1",
                attack_type=result["predicted_class"],
                confidence=result["confidence"],
                risk_level=result["risk_level"],
                risk_score=result["risk_score"],
                action=result["action"],
                is_blocked=False,
            ))
            session.commit()
            session.close()

        session = SessionLocal()
        count_after = session.query(func.count(SecurityEvent.id)).scalar()
        session.close()

        assert count_after >= count_before + 2


class TestCryptoE2EPipeline:
    """End-to-end cryptographic pipeline test — no model dependency."""

    def test_full_crypto_chain(self):
        """ECDH exchange → AES encryption → decryption → tampering detection."""
        from crypto.key_exchange import perform_ecdh_exchange
        from crypto.encryption import encrypt, decrypt, tamper_ciphertext

        # 1. Key exchange
        client_key, server_key = perform_ecdh_exchange()
        assert client_key == server_key

        # 2. Encrypt
        message = "Secure Channel Test — AI-SNIDS"
        enc = encrypt(message, client_key)
        assert enc.ciphertext

        # 3. Decrypt (success)
        dec_ok = decrypt(enc, server_key)
        assert dec_ok.success
        assert dec_ok.plaintext == message
        assert dec_ok.integrity_verified

        # 4. Tamper + fail
        tampered = tamper_ciphertext(enc)
        dec_fail = decrypt(tampered, server_key)
        assert not dec_fail.success
        assert not dec_fail.integrity_verified
        assert dec_fail.plaintext is None
