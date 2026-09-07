"""
crypto/key_exchange.py

Elliptic Curve Diffie-Hellman (ECDH) key exchange implementation.

WHY ECDH?
---------
In secure communication, two parties need to establish a shared secret
over an insecure channel (like the internet) WITHOUT transmitting the
secret itself. This is the key exchange problem.

ECDH solves this using mathematical properties of elliptic curves:

  Client generates:  private_key_A, public_key_A = private_key_A × G
  Server generates:    private_key_B, public_key_B = private_key_B × G

  Client computes:   shared = private_key_A × public_key_B
  Server computes:     shared = private_key_B × public_key_A

  Both arrive at:   private_key_A × private_key_B × G
  Without EVER transmitting private_key_A or private_key_B!

WHY ELLIPTIC CURVES (not RSA)?
--------------------------------
  - ECC (256-bit) provides equivalent security to RSA (3072-bit)
  - Smaller key sizes → faster operations → less CPU/memory
  - P-256 (NIST curve) is NIST-recommended and widely deployed
    (used in TLS 1.3, Signal protocol, modern browsers)

WHY P-256 (SECP256R1)?
-----------------------
  - Well-studied, no known practical attacks
  - Supported by all major TLS implementations
  - Hardware acceleration on modern CPUs

SECURITY NOTES:
---------------
  1. Private keys are NEVER logged, stored in the database, or exposed
     in any API response. They are ephemeral (generated per session).
  2. We use HKDF (Hash-based Key Derivation Function) to derive the
     AES key from the ECDH shared secret — raw shared secrets should
     not be used directly as symmetric keys.
  3. Ephemeral ECDH (ECDHE) means each session uses fresh key pairs,
     providing Perfect Forward Secrecy (PFS): compromising a long-term
     key does NOT compromise past session keys.
"""

import os
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDH,
    SECP256R1,
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey,
    generate_private_key,
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_public_key,
)
from cryptography.hazmat.backends import default_backend


# The AES-256 key length we derive from the ECDH shared secret
AES_KEY_LENGTH = 32  # 256 bits


class ECDHParty:
    """
    Represents one party in an ECDH key exchange.

    Each party:
    1. Generates an ephemeral ECC key pair (private + public)
    2. Shares ONLY the public key with the other party
    3. Derives the same shared AES key from the exchange

    Usage:
        client = ECDHParty(name="Client")
        server   = ECDHParty(name="Server")

        # Exchange public keys
        client.load_peer_public_key(server.get_public_key_bytes())
        server.load_peer_public_key(client.get_public_key_bytes())

        # Both derive the same AES key
        client_key = client.derive_aes_key()
        server_key   = server.derive_aes_key()
        assert client_key == server_key  # ✓ Perfect agreement
    """

    def __init__(self, name: str = "Party"):
        self.name = name
        self._private_key: EllipticCurvePrivateKey = generate_private_key(
            curve=SECP256R1(),
            backend=default_backend(),
        )
        self._peer_public_key: EllipticCurvePublicKey | None = None
        self._shared_secret: bytes | None = None
        self._aes_key: bytes | None = None

    def get_public_key_bytes(self) -> bytes:
        """
        Export our public key in DER format for sharing with the peer.

        DER (Distinguished Encoding Rules) is a binary encoding format
        that is compact and unambiguous — suitable for transmission.

        NOTE: This is our PUBLIC key only. Private key never leaves this object.
        """
        return self._private_key.public_key().public_bytes(
            encoding=Encoding.DER,
            format=PublicFormat.SubjectPublicKeyInfo,
        )

    def get_public_key_hex(self) -> str:
        """Return public key as a hex string for display purposes."""
        return self.get_public_key_bytes().hex()

    def load_peer_public_key(self, peer_public_key_bytes: bytes) -> None:
        """
        Import and store the peer's public key.

        Args:
            peer_public_key_bytes: The peer's DER-encoded public key bytes.
        """
        self._peer_public_key = load_der_public_key(
            peer_public_key_bytes,
            backend=default_backend(),
        )

    def compute_shared_secret(self) -> bytes:
        """
        Perform the ECDH exchange to compute the shared secret.

        The shared secret is a point on the elliptic curve. We extract
        only its X coordinate (standard practice).

        IMPORTANT: The raw shared secret is NOT suitable as an AES key:
        - Its distribution is not uniformly random
        - Key derivation (HKDF) is needed to produce a proper key

        Raises:
            RuntimeError: if peer public key hasn't been loaded yet.
        """
        if self._peer_public_key is None:
            raise RuntimeError(
                f"{self.name}: Cannot compute shared secret without peer public key. "
                "Call load_peer_public_key() first."
            )

        self._shared_secret = self._private_key.exchange(
            ECDH(),
            self._peer_public_key,
        )
        return self._shared_secret

    def derive_aes_key(self, context: bytes = b"ai-snids-aes256gcm") -> bytes:
        """
        Derive an AES-256 key from the ECDH shared secret using HKDF.

        WHY HKDF?
        ---------
        HKDF (RFC 5869) is a key derivation function based on HMAC.
        It takes the raw shared secret and produces a cryptographically
        strong, uniformly distributed key of any desired length.

        Parameters:
        - hash: SHA-256 (256-bit output)
        - length: 32 bytes = 256 bits (for AES-256)
        - salt: None (use HKDF default — production systems would use a
                random salt exchanged alongside the public keys)
        - info: Context label — ensures keys derived for different purposes
                (e.g., AES key vs HMAC key) are independent even from the
                same shared secret.

        Returns:
            32-byte AES-256 key (binary)
        """
        if self._shared_secret is None:
            self.compute_shared_secret()

        hkdf = HKDF(
            algorithm=SHA256(),
            length=AES_KEY_LENGTH,
            salt=None,
            info=context,
            backend=default_backend(),
        )
        self._aes_key = hkdf.derive(self._shared_secret)
        return self._aes_key

    @property
    def aes_key(self) -> bytes:
        """Return the derived AES key (derive it if not yet computed)."""
        if self._aes_key is None:
            self.derive_aes_key()
        return self._aes_key

    def get_summary(self) -> dict:
        """
        Return a safe summary of this party's key exchange state.

        SECURITY: Private key is NEVER included in this summary.
        """
        return {
            "party_name": self.name,
            "public_key_hex": self.get_public_key_hex(),
            "public_key_length_bits": len(self.get_public_key_bytes()) * 8,
            "curve": "P-256 (SECP256R1)",
            "peer_loaded": self._peer_public_key is not None,
            "shared_secret_computed": self._shared_secret is not None,
            "aes_key_derived": self._aes_key is not None,
            # Never log the private key: "private_key": "*** NEVER EXPOSED ***"
        }


def perform_ecdh_exchange() -> tuple[bytes, bytes]:
    """
    Simulate a complete ECDH key exchange between two parties.

    Returns:
        (client_aes_key, server_aes_key) — should be identical bytes.

    Used for demonstration and testing.
    """
    client = ECDHParty("Client")
    server = ECDHParty("Server")

    # Step 1: Exchange public keys (in practice, sent over the network)
    client.load_peer_public_key(server.get_public_key_bytes())
    server.load_peer_public_key(client.get_public_key_bytes())

    # Step 2: Each party independently derives the same AES key
    client_key = client.derive_aes_key()
    server_key = server.derive_aes_key()

    assert client_key == server_key, "ECDH key agreement failed — keys do not match!"

    return client_key, server_key
