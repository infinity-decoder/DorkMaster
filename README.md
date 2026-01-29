# DorkMaster Pro 🔍🕶️

DorkMaster Pro is a high-performance, terminal-based reconnaissance intelligence tool designed for Google Dork management and stealth execution. Inspired by the aesthetics of modern cybersecurity toolkits like Kali Linux, it provides a feature-rich, "Cyberpunk" styled environment for security researchers to scrape, manage, and execute dorks with precision.
<img width="943" height="494" alt="Screenshot 2026-01-29 181552" src="https://github.com/user-attachments/assets/8ca48834-405e-43b0-8bea-e277e426053e" />


<img width="1156" height="623" alt="image" src="https://github.com/user-attachments/assets/f47aab1c-083d-4f34-9610-6dc7157159f4" />

---

## 🚀 Advanced Features

### 📡 Intelligence Gathering
- **Full Database Synchronization**: Reliable scraping of the entire Exploit-DB (GHDB) repository (7000+ dorks) via high-performance AJAX endpoints.
- **Incremental Updates**: Keep your intelligence fresh with targeted updates for the newest dork additions.
- **Serverless JSON Storage**: Optimized local storage using a portable JSON format with $O(1)$ duplicate checking for maximum speed.

### 🕵️ Stealth Search Engine
- **Anti-Bot Mitigation**: Built-in randomized delays (jitters) and User-Agent rotation to stay under Google's radar.
- **Smart 429 Handling**: Proactive detection of rate limiting with specific tactical advice for IP rotation (VPN/Proxy).
- **High-Res Results**: Scrapes live search results with a focus on speed and reliability.

### 🌐 Dual Execution Modes
- **Terminal Execution**: Scrape results directly into your CLI in a secure, controlled environment.
- **Live Browser Mode**: Instantly launch your default web browser and bridge your dork query directly into Google Search.

### 🎨 Premium User Experience
- **Cyberpunk UI**: A vibrant, high-contrast visual theme with icon-enhanced menus and box-drawing banners.
- **Simplified Navigation**: Every sub-menu and details page features a clear **Return to Main Menu** option.
- **Direct Numeric Input**: Support for lightning-fast command execution (type `1-8` for instant action).
- **Persistent Pagination**: The system remembers your page position even when jumping between dork details and list views.
- **In-place Editing**: Modify dork queries on-the-fly with smart pre-filled prompts.

---

## 🛠️ Installation & Rapid Deployment

DorkMaster Pro features an **Automated Setup and Sync** system. Every launch automatically verifies your environment and pulls the latest tactical updates.

### 🪟 Windows Deployment
1. Double-click `run.bat` or execute:
   ```cmd
   run.bat
   ```

### 🐧 Linux / 🍎 macOS Deployment
1. Set execution permissions and launch:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

### 📦 Manual Initialization (If needed)
1. Initialize environment: `python -m venv .venv`
2. Activate:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Launch Hub: `python dorkmaster_pro.py`

---

## 🎯 Main Menu Options

1. **Search for Dorks**: Query the 7000+ local dorks by keyword or title.
2. **Check for New Dorks**: Fetch only the latest additions from GHDB.
3. **Sync Complete GHDB Library**: (Recommended first run) Sync the entire GHDB library.
4. **Browse Dorks by Category**: Explore organized vulnerabilities (Files containing juicy info, etc.).
5. **Quick Execution (Raw Dork)**: Immediately run any dork query without local database lookup.
6. **View System Statistics**: Check dork counts and last synchronization timestamps.
7. **Export Results**: Export results to JSON/CSV (Beta).
8. **Terminate Session**: Securely close the DorkMaster Hub.

---

## ⚖️ Legal & Ethical Policy

**DorkMaster Pro is intended for authorized security research and educational purposes only.** 

Accessing information through Google Dorks can lead to sensitive data exposure. Unauthorized use against targets without prior consent is strictly prohibited and likely illegal in your jurisdiction. The author and contributors are not responsible for any misuse, damage, or legal consequences arising from the use of this tool.

---
**[ infinitydecoder ]** | *Reconnaissance. Refined.*
