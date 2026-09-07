@echo off
REM DorkMaster Local Runner for Windows
cd /d "%~dp0"

IF NOT EXIST ".venv" (
    echo [*] Creating virtual environment in .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [*] Installing dependencies in editable mode...
    python -m pip install --upgrade pip
    pip install -e .
) ELSE (
    call .venv\Scripts\activate.bat
)

echo [*] Launching DorkMaster...
python -m dorkmaster %*
pause
