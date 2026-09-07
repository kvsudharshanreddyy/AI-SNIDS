# 5-Minute Demonstration Script: AI-SNIDS

## Pre-Demo Checklist (do this before the evaluator arrives)

```bash
cd /home/luffy/.gemini/antigravity-ide/scratch/AI-SNIDS

# 1. Ensure model is trained
ls ai/model/rf_model.pkl && echo "✅ Model ready" || python3 ai/train.py

# 2. Start dashboard (keep this terminal open)
streamlit run dashboard/app.py

# 3. Open browser: http://localhost:8501
```

---

## STEP 1 — Open Dashboard (30 seconds)

**Navigate to**: http://localhost:8501

**Show the evaluator:**
- Dark security-themed dashboard
- System Status sidebar: "✅ AI Model: Loaded", "✅ Database: Connected"
- Sidebar navigation: 6 pages

**Say:**
> "This is AI-SNIDS — an AI-Powered Secure Network Intrusion Detection System.
> It combines a machine learning detection engine with a cryptographic communication layer.
> The dashboard connects to a locally running SQLite database and a trained Random Forest model."

---

## STEP 2 — Normal Traffic (45 seconds)

**Click**: 🔍 Traffic Analysis (sidebar)

**Select**: "BENIGN (Normal Web Traffic)"
**Source IP**: 192.168.1.100
**Destination IP**: 10.0.0.1

**Click**: 🔍 Analyze Traffic

**Expected result:**
- Predicted Class: ✅ BENIGN
- Risk Level: 🟢 MONITOR
- Action: ALLOW

**Show the feature vector** (click "📋 View Feature Vector"):
- Flow Duration: ~5.2 million µs
- Flow Packets/s: ~4.2 (typical for HTTP browsing)

**Say:**
> "This represents normal HTTP browsing traffic. The model identifies it as BENIGN with high confidence.
> The risk level is MONITOR — the system allows it through with no action."

---

## STEP 3 — Attack Detection (90 seconds)

### 3a: DDoS Attack

**Select**: "DDoS Attack"
**Source IP**: 10.0.0.55
**Click**: 🔍 Analyze Traffic

**Expected result:**
- Predicted Class: 💥 DDoS
- Confidence: 95%+
- Risk Level: 🔴 HIGH
- Action: BLOCK

**Show the class probability bar chart** — DDoS bar dominates.

**Say:**
> "This represents a DDoS flood. The model detects it with high confidence.
> Key discriminating features: Flow Packets/s is 52,000 — versus 4 for normal traffic.
> All packets are forward-only — 0 backward packets — meaning the server can't respond.
> The risk engine scores this as HIGH and recommends BLOCKING."

### 3b: Port Scan

**Select**: "Port Scan"
**Source IP**: 172.16.0.200
**Click**: 🔍 Analyze Traffic

**Expected result:**
- Predicted Class: 🔎 PortScan
- Risk Level: MEDIUM or HIGH

**Say:**
> "Port scanning is reconnaissance — the attacker is probing which ports are open
> before launching a targeted attack. The model detects the characteristic pattern:
> extremely short flow duration, only 2 packets, 0 bytes returned."

---

## STEP 4 — Dashboard Metrics (30 seconds)

**Click**: 🏠 Dashboard (sidebar)

**Show:**
- Threats Detected counter (incremented)
- Blocked IPs counter (if DDoS was flagged)
- Attack Distribution pie chart

**Click**: 📋 Event Log

**Show:**
- Timestamped security events in the SQLite database
- Each row shows attack type, confidence, risk level, action
- Download CSV button

**Say:**
> "Every detection is persisted to a SQLite database. In a real SOC,
> this would feed into a SIEM like Splunk or Elastic. Here we store it locally
> for audit trails and post-incident analysis."

---

## STEP 5 — Cryptography Demo (90 seconds)

**Click**: 🔐 Cryptography Demo (sidebar)

### 5a: Key Exchange

**Click**: "Generate Key Pairs & Perform Exchange"

**Show:**
- Client's and Server's P-256 public keys (hex)
- Both derived AES keys match ✅

**Say:**
> "Client and Server each generate an ephemeral P-256 key pair.
> They exchange ONLY the public keys — which can be intercepted without risk.
> Each party independently computes the same 256-bit AES key via ECDH.
> The private keys are NEVER transmitted, displayed, or stored."

### 5b: Encryption

**Type in message**: `Hello Secure Network`

**Click**: 🔒 Encrypt Message

**Show:**
- Nonce (96-bit random, base64)
- Ciphertext + auth tag (base64)

**Say:**
> "AES-256-GCM encrypts the message. Notice the nonce — a random 96-bit value
> generated fresh for every message. It's not secret, but it must never repeat
> for the same key. The ciphertext includes a 16-byte authentication tag."

**Click**: 🔓 Decrypt Message

**Show**: `✅ Decryption successful! Recovered: "Hello Secure Network"`

### 5c: Tampering Detection

**Click**: 🔨 Tamper with Ciphertext → Attempt Decryption

**Show:**
- Original vs tampered ciphertext (first byte differs)
- `🚫 INTEGRITY VERIFICATION FAILED: AES-256-GCM authentication tag mismatch detected`

**Say:**
> "I flipped a single bit in the ciphertext. AES-GCM detected the modification
> and REFUSED to return any data. No corrupted plaintext is ever exposed.
> This is the Integrity guarantee of the CIA triad."

---

## STEP 6 — Model Performance (30 seconds)

**Click**: 📊 Model Performance (sidebar)

**Show:**
- Accuracy, Precision, Recall, F1 Score metrics
- Confusion matrix heatmap
- Feature importance chart

**Say:**
> "The model is evaluated with multiple metrics — not just accuracy.
> In cybersecurity, a model that always predicts 'BENIGN' can achieve 95% accuracy
> while detecting zero attacks. Recall measures what fraction of real attacks we caught —
> that's the metric that matters most for an IDS."

**Point to feature importance chart:**
> "The Random Forest tells us WHICH features were most discriminating.
> Flow Duration and Inter-Arrival Times are the top features —
> this gives human analysts actionable insights and builds trust."

---

## STEP 7 — Closing Summary (30 seconds)

**Show the About page** (ℹ️ About in sidebar)

**Say:**
> "AI-SNIDS integrates two complementary security mechanisms:
>
> The AI detection engine protects AVAILABILITY — it detects and responds to
> attacks that would disrupt services.
>
> The cryptographic layer protects CONFIDENTIALITY and INTEGRITY —
> data in transit cannot be read or tampered with.
>
> Together, they address the full CIA triad:
> Confidentiality through AES-256-GCM,
> Integrity through the GCM authentication tag,
> Availability through Random Forest intrusion detection.
>
> This is an academic prototype — it uses a synthetic dataset and simulates
> IP blocking at the application level. In production, this would integrate
> with real firewall rules, live packet streams, and a SIEM platform."

---

## Anticipated Questions and Answers

**Q: Why Random Forest and not deep learning?**
> Random Forest trains in under 1 second on CPU, is interpretable via feature importances,
> handles tabular data well, and is well-suited for academic demonstration.
> Deep learning would need a GPU and much more data for comparable results on this task.

**Q: Why AES-GCM and not AES-CBC?**
> AES-CBC only provides confidentiality — you'd need a separate HMAC for integrity.
> AES-GCM provides both in a single, standardized primitive used in TLS 1.3.
> CBC is also vulnerable to padding oracle attacks if misimplemented.

**Q: Why ECDH and not RSA?**
> ECDH with P-256 provides equivalent security to RSA-3072, but with much smaller keys
> and faster computation. It also supports Perfect Forward Secrecy naturally.

**Q: Why 100% accuracy on synthetic data?**
> The synthetic dataset uses Gaussian distributions per class that are well-separated by design.
> This demonstrates the pipeline works correctly. On real CICIDS2017 data,
> expect 95-99% accuracy with some class confusion — particularly DoS vs DDoS.

**Q: Is this production-ready?**
> No — and we're honest about that. It's an academic prototype.
> Limitations include: 2017-era training data, simulated blocking, no encrypted traffic inspection.
> Future work would address online learning, real firewall integration, and post-quantum cryptography.
