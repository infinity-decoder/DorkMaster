"""
DorkMaster Utilities Module
Provides reusable helpers for XDG compliance, networking, logging, data export,
and terminal formatting adhering to PEP 8 and DRY principles.
"""

import csv
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Realistic User-Agents for anti-bot mitigation
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


class PathManager:
    """Manages application file paths compliant with XDG Base Directory Specification."""

    @staticmethod
    def get_data_dir() -> Path:
        xdg_data = os.environ.get("XDG_DATA_HOME")
        base = Path(xdg_data) if xdg_data else Path.home() / ".local" / "share"
        data_dir = base / "dorkmaster"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @staticmethod
    def get_state_dir() -> Path:
        xdg_state = os.environ.get("XDG_STATE_HOME")
        base = Path(xdg_state) if xdg_state else Path.home() / ".local" / "state"
        state_dir = base / "dorkmaster"
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    @classmethod
    def get_default_db_path(cls) -> Path:
        return cls.get_data_dir() / "dorks.json"

    @classmethod
    def get_default_log_path(cls) -> Path:
        return cls.get_state_dir() / "activity.log"


class Utils:
    """General utility helpers."""

    @staticmethod
    def get_random_user_agent() -> str:
        """Returns a randomized browser User-Agent."""
        return random.choice(USER_AGENTS)

    @staticmethod
    def get_default_headers(extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Generates standard browser request headers with a rotated User-Agent."""
        headers = {
            "User-Agent": Utils.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def sleep_jitter(min_seconds: float = 1.0, max_seconds: float = 2.5) -> None:
        """Randomized sleep interval for throttling and anti-detection."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    @staticmethod
    def check_connectivity(url: str = "https://www.google.com", timeout: float = 5.0) -> bool:
        """Verifies internet connectivity before running network-intensive tasks."""
        try:
            import requests
            response = requests.get(url, headers=Utils.get_default_headers(), timeout=timeout)
            return response.status_code < 500
        except Exception:
            return False

    @staticmethod
    def clear_screen() -> None:
        """Clears terminal screen cross-platform."""
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def log_activity(message: str, log_file: Optional[Path] = None) -> None:
        """Logs timestamped activity messages to state log file."""
        target = log_file or PathManager.get_default_log_path()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(target, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except OSError:
            pass

    @staticmethod
    def export_data(filepath: str | Path, data: List[Dict[str, Any]], format_type: str = "json") -> bool:
        """
        Unified DRY exporter supporting JSON, CSV, and plain TXT files.
        """
        target = Path(filepath).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        fmt = format_type.lower()

        try:
            if fmt == "json":
                with open(target, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True

            elif fmt == "csv":
                if not data:
                    return False
                keys = list(data[0].keys())
                with open(target, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)
                return True

            elif fmt in ("txt", "text"):
                with open(target, "w", encoding="utf-8") as f:
                    for idx, item in enumerate(data, 1):
                        title = item.get("title") or item.get("dork") or item.get("url") or str(item)
                        f.write(f"{idx}. {title}\n")
                        for k, v in item.items():
                            if k not in ("title", "dork"):
                                f.write(f"   {k}: {v}\n")
                        f.write("\n")
                return True

            return False
        except (OSError, TypeError, ValueError) as err:
            Utils.log_activity(f"Export error ({target}): {err}")
            return False

    @staticmethod
    def format_table(data: List[List[Any]], headers: List[str], tablefmt: str = "grid") -> str:
        """Renders formatted ASCII/grid tables using tabulate with graceful fallback."""
        try:
            from tabulate import tabulate
            return tabulate(data, headers=headers, tablefmt=tablefmt)
        except ImportError:
            # Fallback simple table formatter
            lines = [" | ".join(str(h) for h in headers)]
            lines.append("-" * len(lines[0]))
            for row in data:
                lines.append(" | ".join(str(c) for c in row))
            return "\n".join(lines)


def safe_exit(code: int = 0) -> None:
    """Exits the process cleanly without tracebacks."""
    sys.exit(code)
