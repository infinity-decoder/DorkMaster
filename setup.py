import os
import sys
import subprocess
import venv
import platform

def create_venv(venv_dir=".venv"):
    """Creates a virtual environment."""
    if not os.path.exists(venv_dir):
        print(f"[*] Creating virtual environment in {venv_dir}...")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"[*] Virtual environment already exists in {venv_dir}.")

def install_dependencies(venv_dir=".venv"):
    """Installs dependencies from requirements.txt."""
    pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe") if platform.system() == "Windows" else os.path.join(venv_dir, "bin", "pip")
    
    if not os.path.exists("requirements.txt"):
        print("[-] requirements.txt not found. Skipping dependency installation.")
        return

    print("[*] Installing dependencies...")
    try:
        subprocess.check_call([pip_exe, "install", "-r", "requirements.txt"])
        print("[+] Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error installing dependencies: {e}")
        sys.exit(1)

def main():
    venv_dir = ".venv"
    create_venv(venv_dir)
    install_dependencies(venv_dir)
    print("\n[+] Setup complete! You can now run the tool using 'run.bat' (Windows) or 'bash run.sh' (Linux/macOS).")

if __name__ == "__main__":
    main()
