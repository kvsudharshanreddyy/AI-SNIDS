"""
crypto/encryption.py

AES-256-GCM encryption/decryption for AI-SNIDS.

WHY AES-256-GCM?
----------------
AES-GCM (Galois/Counter Mode) is an AUTHENTICATED ENCRYPTION scheme.
This means it provides THREE security properties in a single primitive:

  1. CONFIDENTIALITY: The ciphertext reveals nothing about the plaintext.
     (Guaranteed by AES-CTR mode encryption)

  2. INTEGRITY: Any modification to the ciphertext (even 1 bit) is
     detected during decryption.
     (Guaranteed by the GCM authentication tag — GHASH)

  3. AUTHENTICITY: The receiver can verify the message came from
     someone who holds the correct key.
     (Also guaranteed by the GCM authentication tag)

This is why AES-GCM is the standard in modern TLS 1.3, Signal, and
virtually all modern secure communication protocols.

ALTERNATIVES CONSIDERED:
  - AES-CBC: Only provides confidentiality (not integrity). Vulnerable
    to padding oracle attacks if misimplemented. NOT recommended.
  - AES-CTR: Only provides confidentiality. Requires a separate HMAC
    for integrity.
  - ChaCha20-Poly1305: Also excellent (modern TLS alternative to AES-GCM).
    Preferred on CPUs without AES-NI hardware acceleration.
    We use AES-GCM here as it's more widely recognized academically.

WHY 256-BIT KEY?
----------------
AES supports 128, 192, and 256-bit keys. AES-256 is standard for
high-security applications. The security difference vs AES-128 is
theoretical (no practical attack exists against either), but AES-256
is the NIST recommendation for long-term security and is expected
to remain secure in the post-quantum era for data confidentiality.

WHAT IS A NONCE?
---------------
A "number used once" — a random 96-bit (12-byte) value that must be
unique for every encryption operation using the same key.

  WHY UNIQUE? If the same (key, nonce) pair is used twice, GCM's
  security is catastrophically broken: an attacker can recover the
  XOR of two plaintexts and forge authentication tags. This failure
  mode is well-documented in the "nonce misuse" literature.

  SOLUTION: We generate a fresh cryptographically random nonce for
  every encryption call using os.urandom() (which uses the OS CSPRNG).
  The nonce is NOT secret — it is transmitted alongside the ciphertext.

WHAT IS THE AUTHENTICATION TAG?
--------------------------------
A 16-byte (128-bit) value appended to the ciphertext. During decryption,
GCM recomputes the tag and compares it with the received tag. If they
differ — even by 1 bit — decryption raises InvalidTag and returns nothing.

This is used in the demo to show integrity failure when ciphertext is
tampered with.

SECURITY RULES FOLLOWED:
  - Keys generated via os.urandom() (CSPRNG)
  - Nonces generated fresh per message via os.urandom()
  - Private keys NEVER stored in logs, DB, or API responses
  - No custom cryptographic algorithms (using Python's cryptography library
    which wraps OpenSSL)
  - No hardcoded keys or IVs
"""

import os
import base64
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


# ─── Constants ─────────────────────────────────────────────────────────────────

NONCE_LENGTH = 12   # 96 bits — GCM recommended nonce length (NIST SP 800-38D)
TAG_LENGTH = 16     # 128 bits — default and maximum GCM tag length
KEY_LENGTH = 32     # 256 bits — AES-256


# ─── Data Types ────────────────────────────────────────────────────────────────

@dataclass
class EncryptedMessage:
    """
    Container for an AES-256-GCM encrypted message.

    All fields are base64-encoded bytes for safe transport/display.

    Fields:
        nonce:      Base64-encoded 96-bit random nonce
        ciphertext: Base64-encoded encrypted payload (includes auth tag)
        key_hint:   First 8 hex chars of key fingerprint (NOT the key itself)
    """
    nonce: str        # base64
    ciphertext: str   # base64 (ciphertext + GCM auth tag appended)
    key_hint: str     # partial key fingerprint for debugging only

    def to_dict(self) -> dict:
        return {
            "nonce": self.nonce,
            "ciphertext": self.ciphertext,
            "key_hint": self.key_hint,
            "algorithm": "AES-256-GCM",
            "nonce_length_bits": NONCE_LENGTH * 8,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EncryptedMessage":
        return cls(
            nonce=d["nonce"],
            ciphertext=d["ciphertext"],
            key_hint=d.get("key_hint", "unknown"),
        )


@dataclass
class DecryptionResult:
    """Result of an AES-GCM decryption attempt."""
    success: bool
    plaintext: str | None    # None if decryption failed
    error: str | None        # None if success
    integrity_verified: bool

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "plaintext": self.plaintext,
            "error": self.error,
            "integrity_verified": self.integrity_verified,
        }


# ─── Core Functions ────────────────────────────────────────────────────────────

def encrypt(plaintext: str, key: bytes) -> EncryptedMessage:
    """
    Encrypt a UTF-8 plaintext string using AES-256-GCM.

    Args:
        plaintext: The message to encrypt (UTF-8 string)
        key:       32-byte AES-256 key (must be from a secure source)

    Returns:
        EncryptedMessage with base64-encoded nonce and ciphertext

    Security:
        - Nonce is generated fresh for EVERY call via os.urandom()
        - The ciphertext includes the 16-byte GCM authentication tag
        - The key is validated to be exactly 32 bytes
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(
            f"AES-256 requires a {KEY_LENGTH}-byte key. "
            f"Got {len(key)} bytes."
        )

    # Generate a fresh random nonce — NEVER reuse with the same key
    nonce = os.urandom(NONCE_LENGTH)

    # AESGCM from the cryptography library wraps OpenSSL's AES-GCM.
    # The last 16 bytes of the returned ciphertext ARE the authentication tag.
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # Key fingerprint: first 4 bytes as hex — for display only, NOT secret
    key_hint = key[:4].hex()

    return EncryptedMessage(
        nonce=base64.b64encode(nonce).decode("ascii"),
        ciphertext=base64.b64encode(ciphertext_with_tag).decode("ascii"),
        key_hint=key_hint,
    )


def decrypt(msg: EncryptedMessage, key: bytes) -> DecryptionResult:
    """
    Decrypt an AES-256-GCM encrypted message.

    This function demonstrates:
    1. Successful decryption when key and ciphertext are valid
    2. Authentication failure when the ciphertext has been tampered with

    Args:
        msg:  The EncryptedMessage to decrypt
        key:  The same 32-byte key used during encryption

    Returns:
        DecryptionResult with success flag and either plaintext or error

    Security:
        - If ANY bit of the ciphertext is modified, InvalidTag is raised
        - The authentication tag verification happens automatically
        - Timing attacks are mitigated by OpenSSL's constant-time tag comparison
    """
    if len(key) != KEY_LENGTH:
        raise ValueError(
            f"AES-256 requires a {KEY_LENGTH}-byte key. Got {len(key)} bytes."
        )

    try:
        nonce = base64.b64decode(msg.nonce)
        ciphertext_with_tag = base64.b64decode(msg.ciphertext)

        aesgcm = AESGCM(key)
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

        return DecryptionResult(
            success=True,
            plaintext=plaintext_bytes.decode("utf-8"),
            error=None,
            integrity_verified=True,
        )

    except InvalidTag:
        # GCM authentication failed — ciphertext was tampered with,
        # wrong key was used, or nonce was incorrect.
        return DecryptionResult(
            success=False,
            plaintext=None,
            error=(
                "⚠ INTEGRITY VERIFICATION FAILED: The ciphertext has been "
                "tampered with, or the wrong decryption key was provided. "
                "AES-256-GCM authentication tag mismatch detected."
            ),
            integrity_verified=False,
        )
    except Exception as e:
        return DecryptionResult(
            success=False,
            plaintext=None,
            error=f"Decryption error: {type(e).__name__}: {str(e)}",
            integrity_verified=False,
        )


def tamper_ciphertext(msg: EncryptedMessage) -> EncryptedMessage:
    """
    Flip a bit in the ciphertext to simulate tampering.

    Used in the demo to show that AES-GCM DETECTS tampering.
    Any modification — even a single bit — causes authentication to fail.

    This is the "integrity demonstration" in STEP 7 of the demo scenario.
    """
    raw = bytearray(base64.b64decode(msg.ciphertext))
    # Flip the first byte of the ciphertext (not the tag — tag is at the end)
    raw[0] ^= 0xFF  # XOR with 0xFF inverts all 8 bits
    return EncryptedMessage(
        nonce=msg.nonce,
        ciphertext=base64.b64encode(bytes(raw)).decode("ascii"),
        key_hint=msg.key_hint + " [TAMPERED]",
    )


def generate_random_key() -> bytes:
    """
    Generate a cryptographically random 256-bit AES key.

    Uses os.urandom() which reads from the operating system's
    Cryptographically Secure Pseudo-Random Number Generator (CSPRNG):
    - Linux: /dev/urandom (getrandom syscall)
    - macOS: arc4random
    - Windows: BCryptGenRandom

    WHY NOT USE A PASSWORD DIRECTLY AS A KEY?
    -----------------------------------------
    Passwords are short, human-memorizable, and low-entropy.
    AES keys need 256 bits of entropy.
    Always use PBKDF2, bcrypt, or Argon2 to derive a key from a password.
    Here we generate directly since we use ECDH (high entropy source).
    """
    return os.urandom(KEY_LENGTH)
