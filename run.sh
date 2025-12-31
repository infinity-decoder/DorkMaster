#!/bin/bash
if [ ! -d ".venv" ]; then
    echo "[*] Environment not found. Running setup..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "[-] Setup failed. Please resolve the errors above."
        exit 1
    fi
fi
echo "[*] Launching DorkMaster Pro..."
source .venv/bin/activate
python3 dorkmaster_pro.py
