@echo off
IF NOT EXIST ".venv" (
    echo [*] Environment not found. Running setup...
    python setup.py
)
echo [*] Launching DorkMaster Pro...
.venv\Scripts\python.exe dorkmaster_pro.py
pause
