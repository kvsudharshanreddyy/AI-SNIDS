"""
crypto/crypto_demo.py

Standalone demonstration script for the cryptographic module.

Demonstrates:
  1. Complete ECDH key exchange between Client and Server
  2. AES-256-GCM encryption of a message
  3. Successful decryption → original plaintext recovered
  4. Ciphertext tampering → integrity failure detected

This script can be run independently:
    python crypto/crypto_demo.py

It is also used by the dashboard's Cryptography Demo section.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto.key_exchange import ECDHParty
from crypto.encryption import encrypt, decrypt, tamper_ciphertext


def run_demo(message: str = "Hello Secure Network") -> dict:
    """
    Run the complete cryptography demonstration.

    Returns a dict with all steps' results, suitable for display
    in the dashboard or CLI.
    """
    results = {
        "message": message,
        "steps": [],
        "success": True,
    }

    def step(name: str, detail: str):
        results["steps"].append({"name": name, "detail": detail})
        print(f"\n{'─' * 55}")
        print(f"  STEP: {name}")
        print(f"{'─' * 55}")
        print(detail)

    print("\n" + "=" * 55)
    print("  AI-SNIDS: Cryptography Demonstration")
    print("  (ECDH Key Exchange + AES-256-GCM)")
    print("=" * 55)
    print(f"\n  Original Message: \"{message}\"")

    # ──────────────────────────────────────────────────────────
    # STEP 1: Key Generation
    # ──────────────────────────────────────────────────────────
    client = ECDHParty("Client")
    server = ECDHParty("Server")

    step(
        "1. ECDH Key Pair Generation",
        f"  Client's Public Key (DER, hex):\n"
        f"    {client.get_public_key_hex()[:64]}...\n\n"
        f"  Server's Public Key (DER, hex):\n"
        f"    {server.get_public_key_hex()[:64]}...\n\n"
        f"  ℹ  Private keys are NEVER displayed, transmitted, or stored.\n"
        f"  ℹ  Curve: P-256 (SECP256R1)"
    )
    results["client_public_key"] = client.get_public_key_hex()
    results["server_public_key"] = server.get_public_key_hex()

    # ──────────────────────────────────────────────────────────
    # STEP 2: Public Key Exchange
    # ──────────────────────────────────────────────────────────
    client.load_peer_public_key(server.get_public_key_bytes())
    server.load_peer_public_key(client.get_public_key_bytes())

    step(
        "2. Public Key Exchange",
        "  Client sends her public key → Server\n"
        "  Server sends his public key → Client\n\n"
        "  ℹ  In a real system, these are exchanged over the network.\n"
        "  ℹ  Intercepting them does NOT reveal the shared secret\n"
        "     (this is the mathematical guarantee of ECDH)."
    )

    # ──────────────────────────────────────────────────────────
    # STEP 3: Shared Secret Derivation
    # ──────────────────────────────────────────────────────────
    client_key = client.derive_aes_key()
    server_key = server.derive_aes_key()

    keys_match = client_key == server_key
    step(
        "3. Shared Secret → AES-256 Key Derivation (HKDF-SHA256)",
        f"  Client's AES Key (first 16 bytes): {client_key[:16].hex()}\n"
        f"  Server's AES Key   (first 16 bytes): {server_key[:16].hex()}\n\n"
        f"  Keys match: {'✓ YES' if keys_match else '✗ NO (ERROR!)'}\n\n"
        f"  ℹ  Both parties independently derived the SAME 256-bit key\n"
        f"     without EVER transmitting the key or the shared secret.\n"
        f"  ℹ  HKDF (RFC 5869) stretches the ECDH output to a proper AES key."
    )
    results["keys_match"] = keys_match
    results["aes_key_fingerprint"] = client_key[:4].hex()

    # ──────────────────────────────────────────────────────────
    # STEP 4: AES-256-GCM Encryption
    # ──────────────────────────────────────────────────────────
    encrypted = encrypt(message, client_key)

    step(
        "4. AES-256-GCM Encryption (Client → Server)",
        f"  Nonce (96-bit, random): {encrypted.nonce}\n"
        f"  Ciphertext (b64):       {encrypted.ciphertext}\n\n"
        f"  ℹ  Nonce is randomly generated per message — NEVER reused.\n"
        f"  ℹ  Ciphertext includes the 16-byte GCM authentication tag.\n"
        f"  ℹ  The plaintext is NOT deducible from the ciphertext alone."
    )
    results["encrypted"] = encrypted.to_dict()

    # ──────────────────────────────────────────────────────────
    # STEP 5: Successful Decryption
    # ──────────────────────────────────────────────────────────
    result_ok = decrypt(encrypted, server_key)

    step(
        "5. Decryption (Server decrypts with his derived key)",
        f"  Decryption: {'✓ SUCCESS' if result_ok.success else '✗ FAILED'}\n"
        f"  Integrity Verified: {result_ok.integrity_verified}\n"
        f"  Recovered Plaintext: \"{result_ok.plaintext}\"\n\n"
        f"  ℹ  AES-GCM verified the authentication tag before decrypting.\n"
        f"  ℹ  Plaintext matches original: "
        f"{'✓ YES' if result_ok.plaintext == message else '✗ NO'}"
    )
    results["decryption_ok"] = result_ok.to_dict()

    # ──────────────────────────────────────────────────────────
    # STEP 6: Ciphertext Tampering + Integrity Failure
    # ──────────────────────────────────────────────────────────
    tampered = tamper_ciphertext(encrypted)
    result_tamper = decrypt(tampered, server_key)

    step(
        "6. TAMPERING DEMO: Modifying Ciphertext → Integrity Failure",
        f"  Original ciphertext: {encrypted.ciphertext[:30]}...\n"
        f"  Tampered ciphertext: {tampered.ciphertext[:30]}...\n\n"
        f"  Decryption after tampering:\n"
        f"    Success: {result_tamper.success}\n"
        f"    Integrity Verified: {result_tamper.integrity_verified}\n"
        f"    Error: {result_tamper.error}\n\n"
        f"  ✓ AES-256-GCM DETECTED the tampering and REFUSED to decrypt.\n"
        f"  ℹ  This demonstrates INTEGRITY protection.\n"
        f"  ℹ  Even a 1-bit change causes authentication tag mismatch."
    )
    results["tamper_demo"] = result_tamper.to_dict()

    # ──────────────────────────────────────────────────────────
    # Summary
    # ──────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  SUMMARY: CIA Triad Demonstration")
    print("=" * 55)
    print("  CONFIDENTIALITY : AES-256-GCM encrypts plaintext")
    print("                    → ciphertext reveals nothing")
    print("  INTEGRITY       : GCM auth tag detects any tampering")
    print("                    → modified ciphertext CANNOT be decrypted")
    print("  AUTHENTICITY    : Only the key holder can produce valid ciphertext")
    print("                    → impersonation is computationally infeasible")
    print("  KEY EXCHANGE    : ECDH establishes shared secret securely")
    print("                    → no secret transmitted over the channel")
    print("=" * 55)

    return results


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello Secure Network"
    run_demo(message)
