<p align="center">
   <img src="assets/dorkmaster.png" alt="Dork Master logo" width="220">
</p>

# DorkMaster 🔍🕶️
> **Automated Google Dorking, OSINT Reconnaissance, and Intelligence Management Tool for Linux & Kali Security Suites.**

[![Build and Release Linux Package](https://github.com/Owlopia/DorkMaster/actions/workflows/release.yml/badge.svg)](https://github.com/Owlopia/DorkMaster/actions/workflows/release.yml)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Kali%20%7C%20Debian%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/Owlopia/DorkMaster)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

DorkMaster is a high-performance reconnaissance intelligence tool designed for automated Google Dork management, database synchronization, and stealth OSINT execution. Engineered specifically for Debian and Kali Linux environments, DorkMaster can be executed globally from any terminal path (`dorkmaster`), launched directly from desktop application menus (XFCE, GNOME, KDE, Kali Menu under *Information Gathering*), or compiled into a standard `.deb` package.

---

## 🚀 Key Features

### 📡 Intelligence Gathering
- **Full Database Synchronization**: Reliable scraping of the entire Exploit-DB (GHDB) repository (7,000+ dorks) via high-performance AJAX endpoints.
- **Incremental Updates**: Fetch newest daily and weekly dork additions without re-downloading the entire catalog.
- **XDG Base Directory Compliance**: Safely stores local databases in `~/.local/share/dorkmaster/` and logs in `~/.local/state/dorkmaster/`, fully compliant with Linux multi-user standards.

### 🕵️ Stealth Search Engine & Anti-Detection
- **Anti-Bot Mitigation**: Randomized jitter delays and intelligent User-Agent rotation.
- **Proactive 429 Handling**: Automatic detection of rate limiting with IP rotation recommendations (VPN/Proxy).
- **Dual Execution**: Run queries directly in the terminal or automatically pop results into your default web browser.

### 🐧 Native Kali / Debian Desktop & CLI Integration
- **Global Terminal Command**: Once installed, run `dorkmaster` from any directory in the system.
- **Desktop Application Launcher**: Includes Freedesktop `dorkmaster.desktop` standard spec, searchable in Kali Linux under:
  - `01 - Information Gathering`
  - `03 - Web Application Analysis`
- **Scriptable CLI + Interactive TUI**: Run headless one-liners in shell scripts (`dorkmaster --search "sql"`) or enter the full Cyberpunk TUI menu by typing `dorkmaster`.

---

## 📦 Installation & Deployment Options

### Method 1: Install Pre-Built Debian Package (`.deb`)
Download the `.deb` package from the [Releases](https://github.com/Owlopia/DorkMaster/releases) page:
```bash
sudo dpkg -i DorkMaster_v0.0.1_all.deb
sudo apt-get install -f   # Fix any missing dependencies if needed
```
Now run:
```bash
dorkmaster
```

### Method 2: Install System-Wide via Pip
```bash
git clone https://github.com/Owlopia/DorkMaster.git
cd DorkMaster
pip install .
```
Or install in editable mode for development:
```bash
pip install -e .
```

### Method 3: Build Your Own `.deb` Package (Debian / Kali)
Prerequisites:
```bash
sudo apt-get update
sudo apt-get install -y python3-all python3-setuptools python3-stdeb debhelper dh-python
```
Build `.deb`:
```bash
python3 setup.py --command-packages=stdeb.command bdist_deb
sudo dpkg -i deb_dist/dorkmaster_*.deb
```

### Method 4: Portable / Local Runner
```bash
# Linux / macOS:
chmod +x run.sh
./run.sh

# Windows:
run.bat
```

---

## 💻 Command-Line Interface (CLI) Usage

DorkMaster provides both an interactive Cyberpunk dashboard and a scriptable CLI:

```text
usage: dorkmaster [-h] [-v] [-s KEYWORD] [-q DORK] [-b] [-n COUNT] [--sync]
                  [--update] [--stats] [--data-path PATH]

options:
  -h, --help            Show this help message and exit
  -v, --version         Show program version and exit
  -s KEYWORD, --search KEYWORD
                        Search cached Google dorks by keyword or title
  -q DORK, --query DORK Directly execute a dork query against Google
  -b, --browser         Open search results directly in default web browser
  -n COUNT, --num COUNT Number of results to retrieve (default: 10)
  --sync                Synchronize full Exploit-DB GHDB library into local storage
  --update              Check and fetch newest dork additions incrementally
  --stats               Show statistics, last sync timestamp, and storage locations
  --data-path PATH      Custom path to dorks database JSON file
```

### Quick CLI Examples:

1. **Launch Interactive Cyberpunk Dashboard**:
   ```bash
   dorkmaster
   ```

2. **Search Local Dorks for a Keyword**:
   ```bash
   dorkmaster --search "phpmyadmin"
   ```

3. **Execute a Raw Dork Query and Scrape 15 Results**:
   ```bash
   dorkmaster --query "inurl:admin login" -n 15
   ```

4. **Execute Query in Live Web Browser**:
   ```bash
   dorkmaster --query "filetype:env DB_PASSWORD" --browser
   ```

5. **Sync Full GHDB Database via Terminal Script**:
   ```bash
   dorkmaster --sync
   ```

---

## 🎯 Main Interactive Menu Options

1. **Search for Dorks**: Query 7,000+ local dorks by keyword or title.
2. **Check for New Dorks**: Fetch latest additions from GHDB.
3. **Sync Complete GHDB Library**: Initial sync of all Exploit-DB dorks.
4. **Browse Dorks by Category**: Explore organized vulnerability classes.
5. **Quick Execution (Raw Dork)**: Execute arbitrary dorks directly.
6. **View System Statistics**: Inspect database count, last sync date, and paths.
7. **Export Results**: Save output to JSON/CSV.
8. **Terminate Session**: Gracefully exit the application.

---

## 🔄 Automated CI/CD Releases (GitHub Actions)

Creating a new release for Linux distributions is fully automated:
1. Create and push a Git tag:
   ```bash
   git tag v0.0.1
   git push origin v0.0.1
   ```
2. The GitHub Actions workflow in `.github/workflows/release.yml` triggers automatically:
   - Builds the `.deb` Debian package using `stdeb`.
   - Generates the standard Python wheel (`.whl`) and source tarball (`.tar.gz`).
   - Creates a new GitHub Release with release notes and attaches all build artifacts.

---

## ⚖️ Legal & Ethical Disclaimer

**DorkMaster is intended strictly for authorized security research, penetration testing, and educational purposes.**

Unauthorized access, automated querying, or exploitation against targets without explicit, documented permission is illegal under applicable cybersecurity laws. The authors and contributors assume no liability for misuse, damages, or legal consequences arising from this software.

---

**Author:** [infinitydecoder](https://github.com/infinity-decoder)  
**Organization:** [Owlopia](https://github.com/Owlopia)  
**License:** [MIT](LICENSE)
