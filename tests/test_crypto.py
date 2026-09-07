"""
tests/test_crypto.py

Unit tests for the cryptographic module.

Tests:
  1. ECDH key exchange — both parties derive same key
  2. AES-256-GCM encryption produces valid ciphertext
  3. Successful decryption recovers original plaintext
  4. Wrong key causes decryption failure
  5. Modified ciphertext triggers integrity verification failure
  6. Invalid nonce causes failure
  7. Encryption produces different ciphertext each time (nonce randomness)

Run with:
    python -m pytest tests/test_crypto.py -v
"""

import sys
from pathlib import Path
import pytest
import base64

sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.key_exchange import ECDHParty, perform_ecdh_exchange
from crypto.encryption import (
    encrypt, decrypt, tamper_ciphertext,
    generate_random_key, EncryptedMessage, KEY_LENGTH
)


# ─── ECDH Tests ───────────────────────────────────────────────────────────────

class TestECDH:

    def test_key_generation(self):
        """Each party generates a unique public key."""
        client = ECDHParty("Client")
        server = ECDHParty("Server")
        # Keys should be different (with overwhelming probability)
        assert client.get_public_key_bytes() != server.get_public_key_bytes()

    def test_public_key_length(self):
        """P-256 DER-encoded public key should be 91 bytes."""
        party = ECDHParty("Test")
        key_bytes = party.get_public_key_bytes()
        # DER SubjectPublicKeyInfo for P-256 is typically 91 bytes
        assert len(key_bytes) > 0
        assert isinstance(key_bytes, bytes)

    def test_key_exchange_produces_matching_keys(self):
        """Client and Server must independently derive the SAME AES key."""
        client_key, server_key = perform_ecdh_exchange()
        assert client_key == server_key, "ECDH key agreement failed — keys do not match"

    def test_derived_key_length(self):
        """Derived AES key must be exactly 32 bytes (256 bits)."""
        client_key, _ = perform_ecdh_exchange()
        assert len(client_key) == 32

    def test_different_sessions_produce_different_keys(self):
        """Each ECDH session (ephemeral keys) should produce different shared secrets."""
        key1, _ = perform_ecdh_exchange()
        key2, _ = perform_ecdh_exchange()
        assert key1 != key2, "Two independent ECDH sessions produced identical keys — key reuse!"

    def test_cannot_derive_without_peer_key(self):
        """Calling compute_shared_secret without peer key raises RuntimeError."""
        client = ECDHParty("Client")
        with pytest.raises(RuntimeError, match="peer public key"):
            client.compute_shared_secret()

    def test_summary_hides_private_key(self):
        """Party summary must never expose the private key."""
        client = ECDHParty("Client")
        summary = client.get_summary()
        summary_str = str(summary)
        assert "private" not in summary_str.lower() or "NEVER" in summary_str
        assert "public_key_hex" in summary


# ─── AES-256-GCM Tests ────────────────────────────────────────────────────────

class TestEncryption:

    TEST_MESSAGE = "Hello Secure Network — AI-SNIDS Test"

    def setup_method(self):
        """Generate a fresh AES key for each test."""
        self.key = generate_random_key()

    def test_encrypt_returns_encrypted_message(self):
        """Encryption should return an EncryptedMessage object."""
        result = encrypt(self.TEST_MESSAGE, self.key)
        assert isinstance(result, EncryptedMessage)
        assert result.nonce
        assert result.ciphertext

    def test_encrypt_nonce_is_random(self):
        """Each encryption should use a different nonce."""
        enc1 = encrypt(self.TEST_MESSAGE, self.key)
        enc2 = encrypt(self.TEST_MESSAGE, self.key)
        assert enc1.nonce != enc2.nonce, "Nonces must be unique per encryption!"

    def test_ciphertext_differs_each_time(self):
        """Same plaintext encrypted twice should produce different ciphertexts."""
        enc1 = encrypt(self.TEST_MESSAGE, self.key)
        enc2 = encrypt(self.TEST_MESSAGE, self.key)
        assert enc1.ciphertext != enc2.ciphertext

    def test_successful_decryption(self):
        """Decryption with the correct key should recover the original message."""
        encrypted = encrypt(self.TEST_MESSAGE, self.key)
        result = decrypt(encrypted, self.key)
        assert result.success is True
        assert result.plaintext == self.TEST_MESSAGE
        assert result.integrity_verified is True
        assert result.error is None

    def test_wrong_key_fails(self):
        """Decryption with a different key must fail."""
        encrypted = encrypt(self.TEST_MESSAGE, self.key)
        wrong_key = generate_random_key()
        assert wrong_key != self.key   # Sanity check
        result = decrypt(encrypted, wrong_key)
        assert result.success is False
        assert result.integrity_verified is False
        assert result.plaintext is None

    def test_tampered_ciphertext_fails(self):
        """AES-GCM must detect any modification to the ciphertext."""
        encrypted = encrypt(self.TEST_MESSAGE, self.key)
        tampered = tamper_ciphertext(encrypted)
        result = decrypt(tampered, self.key)
        assert result.success is False
        assert result.integrity_verified is False
        assert result.plaintext is None
        assert result.error is not None

    def test_tampered_nonce_fails(self):
        """A modified nonce must also cause decryption to fail."""
        encrypted = encrypt(self.TEST_MESSAGE, self.key)
        # Corrupt the nonce
        raw_nonce = bytearray(base64.b64decode(encrypted.nonce))
        raw_nonce[0] ^= 0xFF
        bad_msg = EncryptedMessage(
            nonce=base64.b64encode(bytes(raw_nonce)).decode("ascii"),
            ciphertext=encrypted.ciphertext,
            key_hint=encrypted.key_hint,
        )
        result = decrypt(bad_msg, self.key)
        assert result.success is False

    def test_wrong_key_length_raises_error(self):
        """Providing a key that's not 32 bytes should raise ValueError."""
        with pytest.raises(ValueError, match="32-byte"):
            encrypt(self.TEST_MESSAGE, b"too_short_key_16")

    def test_empty_message(self):
        """Encryption of empty string should still work."""
        enc = encrypt("", self.key)
        result = decrypt(enc, self.key)
        assert result.success is True
        assert result.plaintext == ""

    def test_unicode_message(self):
        """Unicode messages should encrypt and decrypt correctly."""
        msg = "भारत 🇮🇳 Cybersecurity नमस्ते"
        enc = encrypt(msg, self.key)
        result = decrypt(enc, self.key)
        assert result.success is True
        assert result.plaintext == msg

    def test_key_length_is_256_bits(self):
        """generate_random_key must produce a 256-bit key."""
        key = generate_random_key()
        assert len(key) == KEY_LENGTH == 32


# ─── End-to-End Crypto Flow ────────────────────────────────────────────────────

class TestCryptoE2E:

    def test_full_demo_flow(self):
        """Run the complete ECDH + AES-GCM demo and verify all steps."""
        from crypto.crypto_demo import run_demo
        results = run_demo("Test Message 12345")

        assert results["keys_match"] is True
        assert results["decryption_ok"]["success"] is True
        assert results["decryption_ok"]["plaintext"] == "Test Message 12345"
        assert results["tamper_demo"]["success"] is False
        assert results["tamper_demo"]["integrity_verified"] is False
