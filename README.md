# DorkMaster Pro 🔍

DorkMaster Pro is a professional-grade, terminal-based reconnaissance tool designed for Google Dork intelligence management and execution. It mimics the style and efficiency of Kali Linux tools, providing a rich CLI interface to scrape, search, and execute Google Dorks.

## 🚀 Features

- **Automated Scraping**: Fetches the latest Google Dorks from Exploit-DB (GHDB).
- **Local Intelligence**: Maintains an offline SQLite database of dorks for lightning-fast searching.
- **Search & Filter**: Search dorks by keywords, titles, or categories.
- **Live Execution**: Run dorks directly from the terminal or edit them before execution.
- **Incremental Updates**: Keep your database fresh with one-click incremental updates.
- **Clean UI**: Interactive menus powered by `questionary` and `colorama`.

## 👤 Author

**infinitydecoder**
- Developed with a focus on ethical hacking and reconnaissance efficiency.

## 🛠️ Installation & Setup

DorkMaster Pro features an automatic setup script that handles environment creation and dependency installation.

### 🪟 Windows
Just double-click `run.bat` or run:
```cmd
run.bat
```

### 🐧 Linux / 🍎 macOS
Run the following command:
```bash
chmod +x run.sh
./run.sh
```

### ⚙️ Manual Setup (Optional)
If you prefer to set things up manually:
1. **Create Venv**: `python -m venv .venv`
2. **Activate**:
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`
3. **Install Deps**: `pip install -r requirements.txt`
4. **Run**: `python dorkmaster_pro.py`

### Main Menu Options:
1. **Search Dorks**: Find specific dorks by keyword.
2. **Update Database**: Scrape latest dorks from Exploit-DB.
3. **Browse by Category**: Explore dorks organized by vulnerability type.
4. **Quick Search**: Manually enter and run any dork.
5. **Database Statistics**: View total dork count and last update time.
6. **Exit**: Securely close the application.

## ⚖️ Legal Disclaimer

This tool is for **authorized security research and educational purposes only**. Unauthorized use against targets without prior consent is illegal. The author is not responsible for any misuse or damage caused by this tool.

---
*Happy Hunting!*
