# Architecture Documentation: AI-SNIDS

## System Overview

AI-SNIDS is a modular, locally-runnable academic prototype demonstrating the integration of:
- AI-based network intrusion detection (Random Forest)
- Cryptographic secure communication (ECDH + AES-256-GCM)
- Security event logging (SQLite)
- Real-time visualization (Streamlit)

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI-SNIDS SYSTEM                             │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   DATA LAYER │    │  AI LAYER    │    │  CRYPTO LAYER    │  │
│  │              │    │              │    │                  │  │
│  │ CICIDS2017   │───▶│ preprocess.py│    │ key_exchange.py  │  │
│  │ (CSV files)  │    │     │        │    │ (ECDH P-256)     │  │
│  │              │    │     ▼        │    │      │           │  │
│  │ Synthetic    │───▶│  train.py   │    │      ▼           │  │
│  │ Generator    │    │ (RF + LR)   │    │ encryption.py    │  │
│  │              │    │     │        │    │ (AES-256-GCM)    │  │
│  │ Scapy Live   │    │     ▼        │    │      │           │  │
│  │ Capture      │    │  predict.py  │    │ crypto_demo.py   │  │
│  │ (optional)   │    │  (risk eng.) │    │                  │  │
│  └──────────────┘    └──────┬───────┘    └────────┬─────────┘  │
│                             │                      │            │
│  ┌──────────────────────────▼──────────────────────▼─────────┐  │
│  │                   PRESENTATION LAYER                       │  │
│  │                                                            │  │
│  │   dashboard/app.py (Streamlit)                            │  │
│  │   ├── 🏠 Dashboard (KPIs + recent threats + charts)       │  │
│  │   ├── 🔍 Traffic Analysis (submit sample → AI classify)   │  │
│  │   ├── 🔐 Crypto Demo (ECDH exchange + AES encrypt/tamper) │  │
│  │   ├── 📊 Model Performance (metrics + plots)              │  │
│  │   ├── 📋 Event Log (SQLite table view + CSV export)       │  │
│  │   └── ℹ️  About (architecture + CIA triad + limitations)   │  │
│  └─────────────────────────────────────────────────────────── ┘  │
│                             │                                   │
│  ┌──────────────────────────▼────────────────────────────────┐  │
│  │                   STORAGE LAYER                            │  │
│  │   data/ai_snids.db (SQLite)                               │  │
│  │   ├── security_events table                               │  │
│  │   └── blocked_ips table                                   │  │
│  └────────────────────────────────────────────────────────── ┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Intrusion Detection

```
1. Input
   ├── CICIDS2017 CSV row (selected in dashboard)
   ├── Synthetic sample (get_attack_samples())
   └── Custom feature values (manual entry)

2. Feature Extraction (network/feature_extraction.py)
   └── 20 flow-level features extracted/validated

3. Preprocessing (ai/preprocess.py — at training time)
   ├── StandardScaler transform (using pre-fitted scaler)
   └── Feature order validated against feature_names.json

4. Model Inference (ai/predict.py)
   ├── rf_model.pkl → predict() → class label
   ├── predict_proba() → probability per class
   └── max probability → confidence score

5. Risk Assessment (ai/predict.py → _assess_risk())
   ├── risk_score = 0.4 × confidence
   │             + 0.4 × ATTACK_SEVERITY[class]
   │             + 0.2 × normalize(packet_rate)
   └── risk_level = HIGH | MEDIUM | LOW | MONITOR

6. Security Response
   ├── HIGH   → action = BLOCK → add to blocked_ips table
   ├── MEDIUM → action = ALERT → display warning
   ├── LOW    → action = LOG  → silent log
   └── MONITOR→ action = ALLOW

7. Logging (database/models.py)
   └── SecurityEvent inserted into SQLite

8. Dashboard Display
   └── Event shown in recent threats + event log table
```

---

## Data Flow: Cryptographic Communication

```
1. Key Generation (per session, ephemeral)
   Client: generate_private_key(SECP256R1) → (priv_A, pub_A)
   Server:   generate_private_key(SECP256R1) → (priv_B, pub_B)

2. Public Key Exchange
   Client sends pub_A (DER-encoded) → Server
   Server sends pub_B (DER-encoded)   → Client
   [Intercepting pub_A or pub_B reveals NOTHING about shared secret]

3. ECDH Computation
   Client: shared = priv_A.exchange(ECDH(), pub_B) → raw bytes
   Server:   shared = priv_B.exchange(ECDH(), pub_A) → same raw bytes
   [priv_A × pub_B == priv_B × pub_A == priv_A × priv_B × G]

4. Key Derivation (HKDF-SHA256, RFC 5869)
   aes_key = HKDF(shared_secret, length=32, hash=SHA256, info="ai-snids-aes256gcm")
   [Maps raw ECDH output → uniformly random 256-bit AES key]

5. Encryption (AES-256-GCM)
   nonce = os.urandom(12)  ← fresh per message
   ciphertext || tag = AESGCM(aes_key).encrypt(nonce, plaintext, None)
   [tag = 128-bit GHASH authentication tag]

6. Transmission
   → nonce (96-bit, public) + ciphertext+tag (base64)

7. Decryption + Verification
   plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext+tag, None)
   [If ANY bit of ciphertext is modified → InvalidTag exception → ABORT]
```

---

## Module Dependency Graph

```
dashboard/app.py
    ├── ai/predict.py
    │   └── ai/preprocess.py (for feature_names)
    │       └── ai/evaluate.py
    ├── crypto/key_exchange.py
    │   └── cryptography.hazmat (OpenSSL)
    ├── crypto/encryption.py
    │   └── cryptography.hazmat (OpenSSL)
    ├── network/feature_extraction.py
    ├── database/database.py
    │   └── database/models.py
    │       └── sqlalchemy
    └── streamlit + plotly + pandas
```

---

## Security Design Decisions

| Decision | Rationale |
|----------|-----------|
| Private keys never stored/logged | Exposure = compromise of all sessions |
| Ephemeral ECDH keys | Perfect Forward Secrecy — past sessions stay secure even if key is later compromised |
| Fresh nonce per encryption | GCM nonce reuse with same key catastrophically breaks confidentiality |
| Application-level IP blocking only | Avoids accidental OS firewall modification in demo environment |
| No custom cryptographic algorithms | Custom crypto is almost always insecure; use vetted standards |
| Scaler fit on training data only | Fitting on all data leaks test statistics → overoptimistic evaluation |
| class_weight='balanced' | Prevents model bias toward majority class (BENIGN dominates raw dataset) |
