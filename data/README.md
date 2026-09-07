"""
data/README.md — Dataset Setup Instructions

=============================================================
AI-SNIDS: CICIDS2017 Dataset Setup
=============================================================

This directory holds the network traffic dataset files used to
train the AI intrusion detection model.

-------------------------------------------------------------
REQUIRED FILES
-------------------------------------------------------------

Download the following CSV files from the CICIDS2017 dataset.
They are publicly available at NO COST from:

  https://www.unb.ca/cic/datasets/ids-2017.html

Look for the section: "CSVs with all flow features"
(or use the Google Drive link provided on that page)

Place the following files directly in this `data/` folder:

  1. Tuesday-WorkingHours.pcap_ISCX.csv
     Size: ~480 MB
     Contains: BENIGN + FTP-Patator + SSH-Patator (Brute Force)

  2. Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
     Size: ~70 MB
     Contains: DDoS + BENIGN

  3. Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
     Size: ~150 MB
     Contains: PortScan + BENIGN

  (Optional — adds DoS classes)
  4. Wednesday-WorkingHours.pcap_ISCX.csv
     Size: ~1.1 GB
     Contains: DoS Hulk, DoS GoldenEye, DoS slowloris, DoS Slowhttptest

-------------------------------------------------------------
DISK USAGE ESTIMATE
-------------------------------------------------------------

Minimum (Files 1-3):     ~700 MB raw CSV
After sampling (20K/class): ~50 MB working set in memory
Trained model (.pkl):    ~30–80 MB

-------------------------------------------------------------
FOLDER STRUCTURE AFTER SETUP
-------------------------------------------------------------

data/
├── README.md                              ← this file
├── Tuesday-WorkingHours.pcap_ISCX.csv
├── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
└── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv

The SQLite database will also be created here automatically:
└── ai_snids.db                            ← auto-created at runtime

-------------------------------------------------------------
IF YOU CANNOT DOWNLOAD THE DATASET
-------------------------------------------------------------

Run the synthetic data generator instead:

  python ai/generate_synthetic.py

This creates:
  data/synthetic_traffic.csv

The model will detect it automatically and use it instead.
The demo will work identically — it just won't use real
network traffic captures.

-------------------------------------------------------------
ACADEMIC NOTE
-------------------------------------------------------------

CICIDS2017 (Canadian Institute for Cybersecurity IDS 2017)
is a widely used benchmark dataset in academic IDS research.

Citation:
  Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani,
  "Toward Generating a New Intrusion Detection Dataset and
  Intrusion Traffic Characterization", 4th International Conference
  on Information Systems Security and Privacy (ICISSP),
  January 2018.
"""
