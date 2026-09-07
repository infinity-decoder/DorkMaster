#!/bin/bash
# DorkMaster Local Runner
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "[*] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "[*] Installing dependencies in editable mode..."
    pip install --upgrade pip
    pip install -e .
else
    source .venv/bin/activate
fi

echo "[*] Launching DorkMaster..."
python3 -m dorkmaster "$@"
