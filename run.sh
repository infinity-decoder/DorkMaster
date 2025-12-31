#!/bin/bash
if [ ! -d ".venv" ]; then
    echo "[*] Environment not found. Running setup..."
    python3 setup.py
fi
echo "[*] Launching DorkMaster Pro..."
source .venv/bin/activate
python3 dorkmaster_pro.py
