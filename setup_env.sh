#!/bin/bash
# setup_env.sh — One-command environment setup for AI-SNIDS
# Usage: bash setup_env.sh

echo "========================================================"
echo "  AI-SNIDS: Environment Setup"
echo "========================================================"

# Install missing packages (system-level with break-system-packages)
echo "[1/3] Installing required Python packages..."
pip3 install --user --break-system-packages \
    fastapi scapy sqlalchemy seaborn python-dotenv 2>&1 | tail -5

echo "[2/3] Copying .env.example to .env (if not exists)..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  → .env created"
else
    echo "  → .env already exists"
fi

echo "[3/3] Generating synthetic dataset..."
python3 ai/generate_synthetic.py

echo ""
echo "========================================================"
echo "  Setup Complete!"
echo "========================================================"
echo ""
echo "  NEXT STEPS:"
echo "  1. Train the model:"
echo "     python3 ai/train.py"
echo ""
echo "  2. Run crypto demo:"
echo "     python3 crypto/crypto_demo.py"
echo ""
echo "  3. Start dashboard:"
echo "     streamlit run dashboard/app.py"
echo ""
echo "  4. Run tests:"
echo "     python3 -m pytest tests/ -v"
echo "========================================================"
