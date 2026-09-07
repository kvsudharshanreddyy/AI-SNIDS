# AI-SNIDS: AI-Powered Secure Network Intrusion Detection and Cryptographic Communication System

> **Academic Prototype** — BTech CSE (AI & ML) | Application Security and Intrusion Detection

[![Python](https://img.shields.io/badge/Python-3.14+-blue)](https://python.org)
[![sklearn](https://img.shields.io/badge/scikit--learn-1.9+-orange)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58+-red)](https://streamlit.io)
[![Tests](https://img.shields.io/badge/Tests-35%20passed-green)]()

---

## 1. Problem Statement

Modern networks face sophisticated attacks — DoS, DDoS, Port Scans, Brute Force, and Botnets — that bypass traditional signature-based detection. Simultaneously, data transmission over untrusted networks requires end-to-end cryptographic security. This project addresses both problems in an integrated academic prototype.

## 2. Objectives

1. Implement AI-based network intrusion detection using a trained Random Forest classifier
2. Analyze and classify network traffic into 5 categories (BENIGN, DoS, DDoS, PortScan, BruteForce)
3. Calculate risk levels and generate appropriate security responses
4. Demonstrate authenticated encryption using ECDH + AES-256-GCM
5. Provide a real-time dashboard for security monitoring
6. Log all events to a persistent SQLite database

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI-SNIDS SYSTEM                          │
├──────────────────────────┬──────────────────────────────────────┤
│   DETECTION PIPELINE     │    CRYPTO COMMUNICATION DEMO         │
│                          │                                      │
│  CICIDS2017 / Synthetic  │  Client A                            │
│          ↓               │     ↓ ECDH key pair (P-256)          │
│  Feature Extraction      │  Exchange public keys                │
│          ↓               │     ↓                                │
│  StandardScaler          │  Derive shared secret (ECDH)         │
│          ↓               │     ↓ HKDF-SHA256                    │
│  Random Forest (100 trees│  AES-256-GCM key (256-bit)           │
│          ↓               │     ↓                                │
│  Attack Class Prediction │  Encrypt (nonce + ciphertext + tag)  │
│          ↓               │     ↓                                │
│  Risk Assessment Engine  │  Decrypt + verify integrity          │
│          ↓               │     ↓                                │
│  SQLite Event Log        │  Plaintext OR integrity error        │
│          ↓               │                                      │
│   Streamlit Dashboard ←──────────────────────────────────────── │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Technologies

| Component | Technology | Why |
|-----------|-----------|-----|
| AI Model | Random Forest (scikit-learn) | Tabular data, interpretable, CPU-friendly, handles imbalance |
| Dataset | CICIDS2017 / Synthetic fallback | Industry-standard IDS benchmark |
| Key Exchange | ECDH P-256 | Smaller keys than RSA, Perfect Forward Secrecy |
| Encryption | AES-256-GCM | Confidentiality + Integrity + Authenticity in one primitive |
| Key Derivation | HKDF-SHA256 | RFC 5869 compliant — uniform key output from shared secret |
| Network Analysis | Scapy | Python-native packet inspection |
| Database | SQLite (SQLAlchemy ORM) | Zero-config, embedded, portable |
| Dashboard | Streamlit | Python-native, zero HTML/CSS overhead |
| Backend | FastAPI (optional) | Type-safe, auto-documented REST API |

## 5. Project Structure

```
AI-SNIDS/
├── README.md
├── requirements.txt
├── .env.example            ← copy to .env
├── setup_env.sh            ← one-command setup
│
├── ai/
│   ├── train.py            ← training pipeline (RF + LR baseline)
│   ├── preprocess.py       ← CICIDS2017 + synthetic data pipeline
│   ├── predict.py          ← inference + risk assessment engine
│   ├── evaluate.py         ← metrics, confusion matrix, feature importance
│   ├── generate_synthetic.py ← fallback dataset generator
│   └── model/              ← saved artifacts (.pkl, .json, .png)
│
├── crypto/
│   ├── key_exchange.py     ← ECDH P-256 + HKDF key derivation
│   ├── encryption.py       ← AES-256-GCM encrypt/decrypt/tamper demo
│   └── crypto_demo.py      ← standalone 6-step demonstration
│
├── network/
│   ├── packet_capture.py   ← Scapy live capture (optional, requires root)
│   └── feature_extraction.py ← feature extraction + sample traffic vectors
│
├── simulation/
│   ├── network.py          ← virtual network topology logic
│   ├── traffic_generator.py← jitter + flow generation
│   ├── scenarios.py        ← attack lab scenarios
│   └── simulator.py        ← AI pipeline simulation coordinator
│
├── database/
│   ├── database.py         ← SQLAlchemy engine, session factory
│   └── models.py           ← SecurityEvent + BlockedIP ORM models
│
├── dashboard/
│   └── app.py              ← Streamlit dashboard (6 pages)
│
├── data/
│   ├── README.md           ← Dataset download instructions
│   └── synthetic_traffic.csv ← Auto-generated when CICIDS2017 unavailable
│
└── tests/
    ├── test_crypto.py      ← 19 crypto tests
    ├── test_ai.py          ← 13 AI/ML tests
    └── test_e2e.py         ← 4 end-to-end pipeline tests
```

## 6. Installation

### Prerequisites
- Python 3.12+ (tested on 3.14.4)
- Linux/macOS/Windows

### Quick Setup

```bash
# Clone / navigate to project
cd AI-SNIDS

# One-command setup (installs dependencies, generates synthetic data)
bash setup_env.sh

# Train the AI model
python3 ai/train.py

# Start the dashboard
streamlit run dashboard/app.py
```

### Manual Installation

```bash
pip3 install --user --break-system-packages \
    scikit-learn numpy pandas matplotlib seaborn \
    cryptography streamlit plotly \
    fastapi uvicorn sqlalchemy scapy python-dotenv
```

## 7. How to Run

### Step 1: Dataset

**Option A — Real CICIDS2017** (recommended for academic authenticity):
1. Download CSV files from: https://www.unb.ca/cic/datasets/ids-2017.html
2. Place in `data/` folder (see `data/README.md` for which files)
3. Run: `python3 ai/train.py`

**Option B — Synthetic data** (works immediately, no download):
```bash
python3 ai/generate_synthetic.py  # auto-runs in setup_env.sh
python3 ai/train.py
```

### Step 2: Train Model
```bash
python3 ai/train.py
```
Output: Model saved to `ai/model/`, evaluation plots generated.

### Step 3: Crypto Demo
```bash
python3 crypto/crypto_demo.py
# or with custom message:
python3 crypto/crypto_demo.py "Hello World"
```

### Step 4: Dashboard
```bash
streamlit run dashboard/app.py
# Opens at: http://localhost:8501
```

### Step 5: Run Tests
```bash
python3 -m pytest tests/ -v
```

## 8. AI Methodology

### Dataset
- **CICIDS2017** (Canadian Institute for Cybersecurity Intrusion Detection System 2017)
- Pre-labeled flow-level features from real network captures
- 5 target classes: BENIGN, DoS, DDoS, PortScan, BruteForce

### Preprocessing Pipeline
1. Load CSV files → concatenate
2. Normalize column names (strip whitespace — CICIDS2017 quirk)
3. Map raw labels to unified class names
4. Remove infinity values (ratio features)
5. Drop rows with NaN
6. Random undersample to 20,000 rows per class (prevent imbalance)
7. Select top 20 features by variance
8. Train/Test split: 80%/20%, stratified
9. StandardScaler (fit on train only — prevents data leakage)

### Model: Random Forest Classifier
- 100 trees, max_depth=20, class_weight='balanced'
- Feature sampling: sqrt(n_features) per split
- All CPU cores used (n_jobs=-1)
- **Why RF?** Ensemble of decision trees handles tabular data, non-linear boundaries, and provides feature importances for explainability

### Evaluation
| Metric | Random Forest | Logistic Regression |
|--------|--------------|---------------------|
| Accuracy | 100% (synthetic) | 99.98% (synthetic) |
| F1 (macro) | 1.000 | 0.9998 |

> **Note**: 100% accuracy on synthetic data is expected — the synthetic distributions are clearly separable by design. On real CICIDS2017 data, expect 95-99% accuracy with some class confusion.

### Risk Assessment Engine
```
Risk Score = 0.4 × Model_Confidence
           + 0.4 × Attack_Severity_Weight
           + 0.2 × Traffic_Intensity

→ Score ≥ 0.70 : HIGH  → BLOCK
→ Score ≥ 0.45 : MEDIUM → ALERT
→ Score ≥ 0.20 : LOW   → LOG
→ Score < 0.20 : MONITOR → ALLOW
```

## 9. Cryptography Methodology

### Key Exchange: ECDH (P-256 / SECP256R1)

```
Client                           Server
─────                           ───
Generate (priv_A, pub_A)        Generate (priv_B, pub_B)
    │                               │
    pub_A ──────────────────────→   │
    │   ←──────────────────────── pub_B
    │                               │
shared = priv_A × pub_B         shared = priv_B × pub_A
    │                               │
    └─── Both = priv_A × priv_B × G ─┘
```

**Key derivation**: HKDF(SHA-256, shared_secret) → 32-byte AES key

### Encryption: AES-256-GCM

```
Input: plaintext, 32-byte key, random 96-bit nonce
Output: ciphertext || 16-byte authentication tag

Decrypt: verify tag first → if mismatch: ABORT
         if valid: return plaintext
```

**Properties demonstrated**:
- ✅ Confidentiality: ciphertext reveals nothing about plaintext
- ✅ Integrity: ANY bit modification causes authentication failure
- ✅ Authenticity: only key holder can produce valid ciphertext

## 10. CIA Triad Mapping

| CIA Property | Implementation | Module |
|-------------|---------------|--------|
| **Confidentiality** | AES-256-GCM encryption | `crypto/encryption.py` |
| **Integrity** | GCM authentication tag (GHASH-128) | `crypto/encryption.py` |
| **Availability** | AI intrusion detection + IP blocklist | `ai/predict.py`, `database/models.py` |

## 11. Testing

```
35 tests total | 35 passed | 0 failed

Cryptography (19 tests):
  ECDH key generation, exchange, PFS
  AES-256-GCM: encrypt, decrypt, wrong key, tampering,
               modified nonce, unicode, edge cases

AI/ML (13 tests):
  Synthetic data generation, predictor loading
  BENIGN/DDoS/PortScan prediction, probability validation
  Risk engine bounds, batch prediction, error handling

End-to-End (4 tests):
  Full pipeline: features → AI → risk → DB → retrieval
  Attack pipeline logging
  Event count verification
  Crypto chain: ECDH → encrypt → decrypt → tamper → fail
```

## 12. Known Limitations

> This is an **academic prototype**. The following limitations apply:

- **Synthetic data**: 100% accuracy is expected on the synthetic dataset — classes are mathematically separable by design. Real CICIDS2017 results will show realistic confusion patterns.
- **Dataset age**: CICIDS2017 (2017) may not represent modern attack techniques (e.g., encrypted C2 channels, AI-generated attacks).
- **Application-level blocking**: IP "blocking" is a prototype simulation. OS firewall rules are NOT modified.
- **Live capture**: Requires root/sudo on Linux. Gracefully degraded to dataset-based demo.
- **Encrypted traffic**: The model analyzes flow-level metadata, not payload. Encrypted traffic payloads cannot be inspected (as designed — privacy protection).
- **Model confidence ≠ absolute certainty**: The risk score is model-derived, not a real threat intelligence feed.

## 13. Future Scope

- Deep learning (LSTM/Transformer) for temporal traffic patterns
- Online learning for concept drift adaptation
- Real-time Scapy streaming integration
- SIEM integration (Splunk, Elastic SIEM)
- Real firewall integration (iptables/nftables)
- Post-quantum cryptography (CRYSTALS-Kyber for key exchange)
- Federated IDS across distributed network nodes
- Zero Trust architecture integration

## 14. References

1. Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). *Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization*. ICISSP 2018.
2. NIST SP 800-38D. *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM)*. 2007.
3. Krawczyk, H., & Eronen, P. (2010). *HMAC-based Extract-and-Expand Key Derivation Function (HKDF)*. RFC 5869.
4. McGrew, D., & Rescorla, E. (2011). *Fundamental Elliptic Curve Cryptography Algorithms*. RFC 6090.
5. Breiman, L. (2001). *Random Forests*. Machine Learning, 45(1), 5–32.

---

*Developed as a CIA micro-project for Application Security and Intrusion Detection.*  
*Python 3.14 | scikit-learn 1.9 | cryptography 46 | Streamlit 1.58*
