# Methodology Documentation: AI-SNIDS

## 1. AI/ML Methodology

### 1.1 Dataset: CICIDS2017

The Canadian Institute for Cybersecurity Intrusion Detection System 2017 dataset was selected because:
- It is the most widely cited academic IDS benchmark (1,000+ citations)
- It contains labeled, flow-level features from real network captures
- It covers diverse, realistic attack scenarios across multiple days
- It is freely available for academic use

**Dataset characteristics:**
- 3 million+ flows across 8 days of capture
- Features: 78 flow-level statistics (packet counts, byte counts, inter-arrival times, etc.)
- Known limitation: 2017-era traffic — modern encrypted C2 channels and AI-generated attacks are not represented

**Files used:**
| File | Classes | Size |
|------|---------|------|
| Tuesday-WorkingHours | BENIGN, FTP-Patator, SSH-Patator | ~480 MB |
| Friday-DDos | BENIGN, DDoS | ~70 MB |
| Friday-PortScan | BENIGN, PortScan | ~150 MB |
| Wednesday (optional) | BENIGN, DoS variants | ~1.1 GB |

### 1.2 Class Mapping

Raw CICIDS2017 has 15 distinct labels. We consolidate to 5:

```
FTP-Patator + SSH-Patator → BruteForce
DoS Hulk + DoS GoldenEye + DoS slowloris + DoS Slowhttptest → DoS
DDoS → DDoS
PortScan → PortScan
BENIGN → BENIGN
```

**Rationale**: Consolidation reduces model complexity while preserving meaningful attack distinctions. An IDS operator can act appropriately on "BruteForce" without needing to distinguish FTP vs SSH specifically.

### 1.3 Preprocessing

#### Missing Value Handling
- Infinity values arise in ratio features (e.g., bytes/second when duration ≈ 0)
- Strategy: replace `inf` / `-inf` with `NaN`, then drop affected rows
- Alternative considered: mean imputation — rejected because inf values indicate degenerate flows, not missing data

#### Class Imbalance
CICIDS2017 is severely imbalanced:
- BENIGN: ~80% of all rows
- Attack classes: individually 0.1%–5%

**Strategy: Random undersampling**
- Sample up to 20,000 rows per class
- Simpler and faster than SMOTE
- Preserves real data statistics (no synthetic interpolation)
- `class_weight='balanced'` in RandomForest provides additional compensation

**Alternatives considered:**
- SMOTE: rejected — generates synthetic interpolations that may not reflect real attack patterns
- Class weights only: would not reduce dataset size, causing memory pressure

#### Feature Selection
- Method: Top-20 features by variance (computed on training set only)
- Removes zero-variance features (constant columns = no discriminating power)
- Final features: Flow Duration, IAT statistics, packet/byte counts, rates

#### Train/Test Split
- 80% train, 20% test
- Stratified: ensures each class has equal representation in both splits
- Random seed: 42 (reproducible)

#### Feature Scaling
- StandardScaler: (x - mean) / std
- **Critical**: Scaler is fit on training data ONLY, then applied to test data
- Fitting on all data (including test) = data leakage = artificially optimistic metrics

### 1.4 Model Selection: Random Forest

**Why not Deep Learning?**
- LSTM/CNN require much more data and training time
- GPU would be needed for practical training time
- Random Forest achieves near-perfect results on tabular flow data
- RF is more interpretable (feature importances, decision paths)

**Why not SVM?**
- SVM with RBF kernel scales poorly (O(n²) to O(n³))
- Training on 100K rows = hours on CPU
- RF trains in seconds

**Why not XGBoost/LightGBM?**
- Could be used as alternatives — similar performance to RF
- RF is more widely taught in curricula, better for academic explanation
- XGBoost would be a valid enhancement in future scope

**Random Forest configuration:**
```python
n_estimators=100      # 100 trees — sweet spot, diminishing returns beyond
max_depth=20          # Prevent overfitting while allowing complex patterns
min_samples_split=5   # Minimum node size
class_weight='balanced' # Compensate for class imbalance
max_features='sqrt'   # sqrt(n_features) features per split — classic RF default
n_jobs=-1             # All CPU cores
random_state=42       # Reproducibility
```

### 1.5 Evaluation Metrics

#### Why not just Accuracy?

Consider a dataset where 95% of traffic is BENIGN:
- A model that predicts "BENIGN" for everything achieves 95% accuracy
- It detects 0 attacks
- This is useless for IDS

Therefore we use:

**Precision** = TP / (TP + FP)
- "Of all traffic I flagged as DDoS, what fraction actually was DDoS?"
- High precision = fewer false alarms = less alert fatigue

**Recall** = TP / (TP + FN)
- "Of all actual DDoS attacks, what fraction did I detect?"
- High recall = fewer missed attacks = better security

**F1 Score** = 2 × (Precision × Recall) / (Precision + Recall)
- Harmonic mean — penalizes extreme imbalance between precision and recall

**For IDS, Recall is typically more critical than Precision:**
- Missing a real attack (false negative) may cause a security breach
- A false alarm (false positive) causes inconvenience but not breach
- However, excessive false positives cause "alert fatigue" — analysts ignore alerts

**Confusion Matrix:**
Shows exactly which classes are confused with each other. For IDS:
- DoS vs DDoS confusion is acceptable (both are denial-of-service)
- BENIGN vs any attack confusion is a miss — most critical error

### 1.6 Risk Assessment Engine

After model prediction, risk is scored as a composite:

```
risk_score = 0.4 × model_confidence
           + 0.4 × attack_severity_weight
           + 0.2 × traffic_intensity_normalized

where:
  BENIGN severity     = 0.0
  BruteForce severity = 0.5
  PortScan severity   = 0.4
  DoS severity        = 0.7
  DDoS severity       = 0.8
  Botnet severity     = 0.9

  traffic_intensity = min(packets_per_second / 100,000, 1.0)
```

**Risk Levels:**
- score ≥ 0.70 → HIGH → BLOCK
- score ≥ 0.45 → MEDIUM → ALERT
- score ≥ 0.20 → LOW → LOG
- score < 0.20 → MONITOR → ALLOW

**Why a composite score (not just model confidence)?**
A PortScan with 95% model confidence is less dangerous than a DDoS at 70% confidence. Confidence measures statistical certainty; severity measures real-world impact. A production IDS would also incorporate threat intelligence feeds, asset criticality, and historical IP reputation.

---

## 2. Cryptography Methodology

### 2.1 Key Exchange: ECDH (Elliptic Curve Diffie-Hellman)

**Problem it solves**: Two parties need a shared secret but cannot send it over the network (it would be intercepted).

**Mathematical basis:**
- Elliptic curve: y² = x³ + ax + b (over a prime field)
- Generator point G is a public constant on the curve
- Private key: random integer k (kept secret)
- Public key: k × G (point multiplication — computationally easy)
- Shared secret: priv_A × pub_B = priv_A × priv_B × G = priv_B × pub_A

**Security basis**: The Elliptic Curve Discrete Logarithm Problem (ECDLP)
- Given G and pub_A = k × G, computing k is computationally infeasible
- Best known attack: ~2^128 operations for P-256 (comparable to AES-128)

**Why P-256 (SECP256R1)?**
- NIST recommended curve
- Supported natively by all modern TLS implementations
- Hardware acceleration on most modern CPUs (Intel/AMD)
- Well-studied — no known backdoors (unlike Dual_EC_DRBG)
- 256-bit key ≈ 128-bit classical security level

**Perfect Forward Secrecy (PFS):**
- New key pairs are generated fresh for each session (ephemeral)
- Compromise of a long-term key does NOT expose past session keys
- This is why ECDHE (ephemeral) is used in TLS 1.3

### 2.2 Key Derivation: HKDF (RFC 5869)

**Why not use the ECDH output directly as AES key?**
1. ECDH output is a point on an elliptic curve — its X coordinate
2. X coordinate may not be uniformly distributed
3. Cryptographic keys must be uniformly random
4. HKDF extracts and expands the shared secret into a proper key

**HKDF construction:**
```
PRK = HMAC-Hash(salt, shared_secret)           # Extract
OKM = HMAC-Hash(PRK, info || counter)          # Expand
```
- hash: SHA-256
- length: 32 bytes (AES-256)
- info: "ai-snids-aes256gcm" (context label)

### 2.3 Encryption: AES-256-GCM

**Why GCM (Galois/Counter Mode)?**

AES-GCM = AES-CTR (confidentiality) + GHASH (integrity + authenticity)

Other modes comparison:
| Mode | Confidentiality | Integrity | Authenticity | Notes |
|------|----------------|-----------|-------------|-------|
| AES-ECB | ✗ | ✗ | ✗ | Patterns visible in ciphertext |
| AES-CBC | ✅ | ✗ | ✗ | Padding oracle attacks possible |
| AES-CTR | ✅ | ✗ | ✗ | Requires separate MAC |
| AES-GCM | ✅ | ✅ | ✅ | Standard AEAD, used in TLS 1.3 |
| ChaCha20-Poly1305 | ✅ | ✅ | ✅ | Better without AES-NI hardware |

**The Nonce:**
- 96 bits (12 bytes) — NIST recommended for GCM
- Generated via `os.urandom(12)` (CSPRNG) — never predictable
- Unique per (key, message) pair — **nonce reuse is catastrophic**
- If nonce is reused: attacker can XOR two ciphertexts to get XOR of plaintexts
- Not secret — transmitted alongside ciphertext

**The Authentication Tag:**
- 128 bits (16 bytes)
- Computed via GHASH over (nonce, ciphertext, associated data)
- Appended to ciphertext
- Decryption verifies tag BEFORE returning plaintext
- Tag mismatch → `InvalidTag` exception → no corrupted data returned

**Integrity Demonstration:**
We flip one byte in the ciphertext:
```python
raw[0] ^= 0xFF   # XOR with 0xFF = invert all 8 bits
```
Result: Decryption raises `InvalidTag` — demonstrating that AES-256-GCM detects **any** modification.

---

## 3. Network Analysis Methodology

### 3.1 Flow-Level Features

Network traffic is analyzed at the **flow level**, not packet level:
- A flow = all packets sharing (src_ip, dst_ip, src_port, dst_port, protocol)
- Flow-level statistics capture behavioral patterns across multiple packets
- This is how CICFlowMeter generates CICIDS2017 features

**Key features and their discriminating value:**

| Feature | Why it discriminates |
|---------|---------------------|
| Flow Duration | DoS/DDoS flows are very short; browsing flows are longer |
| Flow Packets/s | DDoS: 50,000+/s; browsing: 4-5/s |
| Total Fwd Packets | PortScan: 2 packets; DoS: 500+ packets |
| Bwd Packet count | PortScan has 0 backward packets (no response) |
| Fwd Packet Mean | DDoS uses full MTU (1514 bytes); brute force uses small packets |
| Flow IAT Mean | DoS has microsecond IAT; browsing has second-level IAT |

### 3.2 Live Capture (Optional)

Scapy provides packet-level access:
- `sniff()` captures packets matching a BPF filter
- Packets are grouped into flow windows (50 packets per window)
- Flow statistics are extracted and fed to the AI predictor
- **Requires root/sudo** on Linux (OS-level packet capture)

For demo purposes, the system uses dataset-based samples — allowing full demonstration without requiring elevated privileges or live attack traffic.
