"""
DorkMaster Core Module
Consolidated OSINT dorking engine, database manager, and scraper algorithms.
Adheres strictly to PEP 8, DRY principles, and robust exception handling.
"""

import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from dorkmaster.banner import display_banner
from dorkmaster.utils import PathManager, Utils

# Color handling with graceful fallback
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    CYAN = Style.BRIGHT + Fore.CYAN
    GREEN = Style.BRIGHT + Fore.GREEN
    YELLOW = Style.BRIGHT + Fore.YELLOW
    RED = Style.BRIGHT + Fore.RED
    MAGENTA = Style.BRIGHT + Fore.MAGENTA
    BLUE = Style.BRIGHT + Fore.BLUE
    WHITE = Style.BRIGHT + Fore.WHITE
    RESET = Style.RESET_ALL
except ImportError:
    CYAN = GREEN = YELLOW = RED = MAGENTA = BLUE = WHITE = RESET = ""


class DorkDatabase:
    """Manages persistent storage, filtering, and indexing of Google Dorks."""

    def __init__(self, db_path: Optional[str | Path] = None):
        self.db_path = Path(db_path) if db_path else PathManager.get_default_db_path()
        self.dorks: List[Dict[str, Any]] = []
        self._seen_ids: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """Loads database from disk or seeds from local project templates."""
        if not self.db_path.exists():
            # Seed from package data or local project data directory if present
            seed_candidates = [
                Path(__file__).resolve().parent / "data" / "dorks.json",
                Path(__file__).resolve().parent.parent / "data" / "dorks.json",
                Path("/usr/share/dorkmaster/dorks.json"),
            ]
            for seed_candidate in seed_candidates:
                if seed_candidate.is_file():
                    try:
                        with open(seed_candidate, "r", encoding="utf-8") as f:
                            self.dorks = json.load(f)
                        self._reindex()
                        self.save()
                        return
                    except (OSError, json.JSONDecodeError):
                        pass
            self.dorks = []
            return

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.dorks = json.load(f)
            self._reindex()
        except (OSError, json.JSONDecodeError) as err:
            Utils.log_activity(f"Failed to read database {self.db_path}: {err}")
            self.dorks = []

    def _reindex(self) -> None:
        """Reconstructs the O(1) duplicate lookup index."""
        self._seen_ids = {
            str(item.get("id") or item.get("dork") or item.get("url_title"))
            for item in self.dorks
            if item
        }

    def save(self) -> bool:
        """Persists dorks into storage atomically."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            tmp_path = self.db_path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.dorks, f, indent=2, ensure_ascii=False)
            tmp_path.replace(self.db_path)
            return True
        except OSError as err:
            Utils.log_activity(f"Database save error: {err}")
            return False

    def add_dorks(self, new_items: List[Dict[str, Any]]) -> int:
        """Adds unique dorks using set index in O(1) time complexity."""
        added_count = 0
        for item in new_items:
            item_id = str(item.get("id") or item.get("dork") or item.get("url_title"))
            if item_id and item_id not in self._seen_ids:
                self.dorks.append(item)
                self._seen_ids.add(item_id)
                added_count += 1
        if added_count > 0:
            self.save()
        return added_count

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Case-insensitive search across dork queries, titles, and categories."""
        q = query.lower().strip()
        if not q:
            return self.dorks
        return [
            item for item in self.dorks
            if q in str(item.get("dork", "")).lower()
            or q in str(item.get("url_title", "")).lower()
            or q in str(item.get("category", "")).lower()
        ]

    def get_categories(self) -> List[str]:
        """Returns sorted list of distinct dork categories."""
        categories = {
            str(item.get("category", "General")).strip()
            for item in self.dorks
            if item.get("category")
        }
        return sorted(categories)

    def filter_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filters dorks matching a specific category."""
        cat_lower = category.lower().strip()
        return [
            item for item in self.dorks
            if str(item.get("category", "")).lower().strip() == cat_lower
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Returns database metadata and operational stats."""
        stats = {
            "total_dorks": len(self.dorks),
            "db_path": str(self.db_path),
            "last_modified": "Unknown",
            "categories_count": len(self.get_categories()),
        }
        if self.db_path.exists():
            try:
                mtime = os.path.getmtime(self.db_path)
                stats["last_modified"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except OSError:
                pass
        return stats


class DorkScraper:
    """Exploit-DB Google Hacking Database (GHDB) scraper with live and archive synchronization."""

    GHDB_URL = "https://www.exploit-db.com/google-hacking-database"
    GHDB_ARCHIVE_URL = "https://gitlab.com/exploit-database/exploitdb/-/raw/main/ghdb.xml"

    @staticmethod
    def _clean_html(raw_html: str) -> str:
        """Strips HTML anchor tags and entities to return clean text."""
        if not raw_html:
            return ""
        clean = re.sub(r"<[^>]+>", "", str(raw_html))
        return html.unescape(clean).strip()

    @classmethod
    def _parse_row(cls, row: Any) -> Optional[Dict[str, Any]]:
        """Parses a single row from either modern dict or legacy list/tuple structure."""
        if isinstance(row, dict):
            dork_id = str(row.get("id", ""))
            date = str(row.get("date", ""))
            raw_title = str(row.get("url_title", ""))
            cat = row.get("category", {})
            if isinstance(cat, dict):
                cat_name = cat.get("cat_title") or "General"
            elif isinstance(row.get("cat_id"), list) and len(row["cat_id"]) > 1:
                cat_name = str(row["cat_id"][1])
            else:
                cat_name = str(row.get("category") or "General")

            author = row.get("author", {})
            if isinstance(author, dict):
                author_name = author.get("name") or "Unknown"
            elif isinstance(row.get("author_id"), list) and len(row["author_id"]) > 1:
                author_name = str(row["author_id"][1])
            else:
                author_name = str(row.get("author") or "Unknown")

        elif isinstance(row, (list, tuple)):
            dork_id = str(row[0]) if len(row) > 0 else ""
            date = str(row[1]) if len(row) > 1 else ""
            raw_title = str(row[2]) if len(row) > 2 else ""
            cat_name = str(row[3]) if len(row) > 3 else "General"
            author_name = str(row[4]) if len(row) > 4 else "Unknown"
        else:
            return None

        query = cls._clean_html(raw_title)
        if not query:
            return None

        return {
            "id": dork_id,
            "date": date,
            "url_title": query,
            "dork": query,
            "category": cat_name,
            "author": author_name,
        }

    @classmethod
    def fetch_batch(cls, start: int = 0, length: int = 500) -> Tuple[List[Dict[str, Any]], int]:
        """
        Fetches a paginated batch from Exploit-DB's AJAX endpoint.
        Returns: (items, total_records)
        """
        headers = {
            "User-Agent": Utils.get_random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": cls.GHDB_URL,
            "Accept-Language": "en-US,en;q=0.9",
        }
        params = {
            "draw": "1",
            "columns[0][data]": "date",
            "start": str(start),
            "length": str(length),
        }

        raw_json = None
        # Try requests if installed
        try:
            import requests
            response = requests.get(cls.GHDB_URL, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            raw_json = response.json()
        except Exception:
            # Fallback to standard library urllib
            try:
                query_str = urllib.parse.urlencode(params)
                full_url = f"{cls.GHDB_URL}?{query_str}"
                req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw_json = json.loads(resp.read().decode("utf-8", errors="ignore"))
            except Exception as err:
                Utils.log_activity(f"GHDB fetch batch error (start={start}): {err}")
                return [], 0

        if not raw_json:
            return [], 0

        records = raw_json.get("data", [])
        try:
            total_records = int(raw_json.get("recordsTotal", 0))
        except (ValueError, TypeError):
            total_records = len(records)

        parsed_items: List[Dict[str, Any]] = []
        for row in records:
            item = cls._parse_row(row)
            if item:
                parsed_items.append(item)

        return parsed_items, total_records

    @classmethod
    def fetch_archive_feed(cls) -> List[Dict[str, Any]]:
        """Fallback fetching from official Exploit-DB repository XML feed."""
        headers = {"User-Agent": Utils.get_random_user_agent()}
        items: List[Dict[str, Any]] = []
        try:
            req = urllib.request.Request(cls.GHDB_ARCHIVE_URL, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                tree = ET.parse(resp)
                root = tree.getroot()
                for entry in root.findall("entry"):
                    dork_id = entry.findtext("id", "").strip()
                    date = entry.findtext("date", "").strip()
                    q = entry.findtext("query") or entry.findtext("shortDescription", "")
                    query = html.unescape(q).strip() if q else ""
                    category = entry.findtext("category", "General").strip()
                    author = entry.findtext("author", "anonymous").strip()
                    if query:
                        items.append({
                            "id": dork_id,
                            "date": date,
                            "url_title": query,
                            "dork": query,
                            "category": category,
                            "author": author,
                        })
        except Exception as err:
            Utils.log_activity(f"GHDB archive fetch error: {err}")
        return items

    @classmethod
    def sync_all(cls, db: DorkDatabase, batch_size: int = 500, max_pages: Optional[int] = None) -> int:
        """Performs full synchronization of the GHDB repository."""
        print(f"{CYAN}[*] Contacting Exploit-DB GHDB repository ({cls.GHDB_URL})...{RESET}")
        initial_batch, total = cls.fetch_batch(start=0, length=batch_size)
        total_added = 0

        if initial_batch:
            total_added += db.add_dorks(initial_batch)
            print(f"{GREEN}[+] Connected to Exploit-DB. First batch ({len(initial_batch)} dorks). Repository size: ~{total}{RESET}")

            start = batch_size
            page = 1
            while start < total:
                if max_pages and page >= max_pages:
                    break
                Utils.sleep_jitter(0.3, 0.6)
                items, _ = cls.fetch_batch(start=start, length=batch_size)
                if not items:
                    break
                added = db.add_dorks(items)
                total_added += added
                start += batch_size
                page += 1
                print(f"\r{CYAN}[*] Progress: {min(start, total)} / {total} dorks synchronized...{RESET}", end="", flush=True)
            print()
        else:
            print(f"{YELLOW}[!] Live Exploit-DB web scraping unavailable or blocked.{RESET}")
            print(f"{CYAN}[*] Synchronizing from official Exploit-DB repository archive...{RESET}")
            archive_items = cls.fetch_archive_feed()
            if archive_items:
                total_added = db.add_dorks(archive_items)
                print(f"{GREEN}[+] Synchronized {len(archive_items)} dorks from Exploit-DB repository archive.{RESET}")
            else:
                print(f"{RED}[-] Failed to reach both live Exploit-DB and repository archive.{RESET}")

        print(f"\n{GREEN}[✓] Sync complete. Added {total_added} new dorks. Total in database: {len(db.dorks)}{RESET}")
        return total_added


class DorkSearcher:
    """Executes Google Dork queries with anti-bot mitigation and browser support."""

    @staticmethod
    def build_google_url(query: str, num: int = 10) -> str:
        encoded = urllib.parse.quote_plus(query)
        return f"https://www.google.com/search?q={encoded}&num={num}"

    @classmethod
    def open_in_browser(cls, query: str) -> bool:
        """Opens search query directly in the user's default browser."""
        url = cls.build_google_url(query)
        print(f"{CYAN}[*] Google Search URL: {RESET}{url}")
        try:
            opened = webbrowser.open(url)
            if not opened:
                print(f"{YELLOW}[!] Notice: Could not trigger system graphical browser automatically. Copy URL above.{RESET}")
            return opened
        except Exception as err:
            Utils.log_activity(f"Failed to open browser: {err}")
            print(f"{YELLOW}[!] Browser execution notice ({err}). URL is available above.{RESET}")
            return False

    @classmethod
    def search(cls, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """
        Executes Google search query and extracts result links.
        Attempts to use googlesearch-python or standard requests parsing.
        """
        results: List[Dict[str, str]] = []
        url = cls.build_google_url(query, num_results)

        # 1. Try googlesearch library if installed
        try:
            from googlesearch import search as gsearch
            for link in gsearch(query, num_results=num_results, sleep_interval=2):
                results.append({"title": link, "url": link, "snippet": ""})
            if results:
                return results
        except ImportError:
            pass
        except Exception as err:
            if "429" in str(err):
                print(f"{RED}[!] Google rate-limit encountered (HTTP 429). Use a VPN/proxy or try --browser mode.{RESET}")
                return []

        # 2. Resilient HTTP parser with standard library urllib fallback
        html_content = ""
        try:
            try:
                import requests
                headers = Utils.get_default_headers()
                Utils.sleep_jitter(0.3, 0.8)
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 429:
                    print(f"{RED}[!] Google rate-limit encountered (HTTP 429). Use --browser mode.{RESET}")
                    return []
                resp.raise_for_status()
                html_content = resp.text
            except ImportError:
                # Standard library zero-dependency fallback
                req = urllib.request.Request(url, headers=Utils.get_default_headers())
                with urllib.request.urlopen(req, timeout=10) as response:
                    html_content = response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as http_err:
            if http_err.code == 429:
                print(f"{RED}[!] Google rate-limit encountered (HTTP 429). Use --browser mode.{RESET}")
            else:
                print(f"{RED}[-] Search HTTP error: {http_err}{RESET}")
            return []
        except Exception as err:
            Utils.log_activity(f"Search request notice: {err}")
            print(f"{RED}[-] Search request notice: {err}{RESET}")
            return []

        if html_content:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/url?q="):
                        actual_url = href.split("/url?q=")[1].split("&")[0]
                        if not actual_url.startswith("https://support.google.com") and not actual_url.startswith("https://accounts.google.com"):
                            title = a.get_text(strip=True) or actual_url
                            results.append({"title": title, "url": actual_url, "snippet": ""})
                    elif href.startswith("http") and "google.com" not in href:
                        title = a.get_text(strip=True) or href
                        results.append({"title": title, "url": href, "snippet": ""})
                    if len(results) >= num_results:
                        break
            except ImportError:
                # Zero-dependency regex extraction
                link_pattern = re.findall(r'<a[^>]+href=["\'](/url\?q=[^"\']+|https?://[^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.IGNORECASE)
                for href, raw_title in link_pattern:
                    clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                    if href.startswith("/url?q="):
                        actual_url = href.split("/url?q=")[1].split("&")[0]
                        if "google.com" not in actual_url:
                            results.append({"title": clean_title or actual_url, "url": actual_url, "snippet": ""})
                    elif href.startswith("http") and "google.com" not in href:
                        results.append({"title": clean_title or href, "url": href, "snippet": ""})
                    if len(results) >= num_results:
                        break

        return results


class DorkMaster:
    """Primary application controller and interactive TUI orchestrator."""

    def __init__(self, data_path: Optional[str] = None):
        self.db = DorkDatabase(data_path)

    def interactive_menu(self) -> None:
        """Main terminal Cyberpunk interactive loop."""
        while True:
            Utils.clear_screen()
            display_banner()
            stats = self.db.get_stats()
            print(f"{BLUE}┌──({WHITE}DorkMaster v0.0.1{BLUE})-[{WHITE}Cached Dorks: {stats['total_dorks']}{BLUE}]")
            print(f"{BLUE}└─▶{RESET}")
            print(f"{CYAN} [1] Search Local Dorks Database{RESET}")
            print(f"{CYAN} [2] Synchronize Exploit-DB GHDB Repository{RESET}")
            print(f"{CYAN} [3] Browse Dorks by Vulnerability Category{RESET}")
            print(f"{CYAN} [4] Execute Direct Dork Query (Terminal / Browser){RESET}")
            print(f"{CYAN} [5] System Information & Storage Statistics{RESET}")
            print(f"{CYAN} [6] Export Local Dorks Database (JSON / CSV / TXT){RESET}")
            print(f"{RED} [0] Exit DorkMaster{RESET}\n")

            try:
                choice = input(f"{YELLOW}dorkmaster > {RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{GREEN}[*] Session terminated.{RESET}")
                break

            if choice in ("0", "q", "exit"):
                print(f"{GREEN}[*] Exiting DorkMaster. Good hunting!{RESET}")
                break
            elif choice == "1":
                self._menu_search()
            elif choice == "2":
                self._menu_sync()
            elif choice == "3":
                self._menu_categories()
            elif choice == "4":
                self._menu_direct_query()
            elif choice == "5":
                self._menu_stats()
            elif choice == "6":
                self._menu_export()
            else:
                input(f"{RED}[-] Invalid option. Press Enter to continue...{RESET}")

    def _menu_search(self) -> None:
        try:
            kw = input(f"\n{YELLOW}Enter search keyword or dork query: {RESET}").strip()
            if not kw:
                return
            results = self.db.search(kw)
            self._display_results_paged(results, title=f"Search: '{kw}'")
        except (KeyboardInterrupt, EOFError):
            return

    def _menu_sync(self) -> None:
        try:
            confirm = input(f"\n{YELLOW}Start full Exploit-DB synchronization? (y/N): {RESET}").strip().lower()
            if confirm in ("y", "yes"):
                DorkScraper.sync_all(self.db)
            input(f"\n{CYAN}Press Enter to return to menu...{RESET}")
        except (KeyboardInterrupt, EOFError):
            return

    def _menu_categories(self) -> None:
        cats = self.db.get_categories()
        if not cats:
            print(f"{RED}[-] No categories available. Synchronize GHDB first.{RESET}")
            input(f"{CYAN}Press Enter to return to menu...{RESET}")
            return

        print(f"\n{GREEN}Available Categories:{RESET}")
        for idx, cat in enumerate(cats, 1):
            print(f" {CYAN}[{idx}]{RESET} {cat}")

        try:
            sel = input(f"\n{YELLOW}Select category number (or Enter to cancel): {RESET}").strip()
            if not sel or not sel.isdigit():
                return
            idx = int(sel) - 1
            if 0 <= idx < len(cats):
                chosen = cats[idx]
                results = self.db.filter_by_category(chosen)
                self._display_results_paged(results, title=f"Category: {chosen}")
        except (KeyboardInterrupt, EOFError):
            return

    def _menu_direct_query(self) -> None:
        try:
            dork = input(f"\n{YELLOW}Enter Google Dork: {RESET}").strip()
            if not dork:
                return
            self._modify_and_execute(dork)
        except (KeyboardInterrupt, EOFError):
            return

    def _menu_stats(self) -> None:
        stats = self.db.get_stats()
        rows = [
            ["Total Dorks Cached", stats["total_dorks"]],
            ["Categories Indexed", stats["categories_count"]],
            ["Database Location", stats["db_path"]],
            ["Last Synchronized", stats["last_modified"]],
            ["Log File Location", str(PathManager.get_default_log_path())],
        ]
        print(f"\n{GREEN}=== DorkMaster Storage & System Stats ==={RESET}")
        print(Utils.format_table(rows, headers=["Property", "Value"]))
        input(f"\n{CYAN}Press Enter to return to menu...{RESET}")

    def _menu_export(self) -> None:
        if not self.db.dorks:
            print(f"{RED}[-] Database is empty. Nothing to export.{RESET}")
            input(f"{CYAN}Press Enter to continue...{RESET}")
            return

        try:
            fmt = input(f"\n{YELLOW}Select export format (json / csv / txt) [json]: {RESET}").strip().lower() or "json"
            default_name = f"dorks_export.{fmt}"
            out = input(f"{YELLOW}Destination file path [{default_name}]: {RESET}").strip() or default_name

            if Utils.export_data(out, self.db.dorks, format_type=fmt):
                print(f"{GREEN}[✓] Successfully exported {len(self.db.dorks)} dorks to {out}{RESET}")
            else:
                print(f"{RED}[-] Export failed.{RESET}")
            input(f"\n{CYAN}Press Enter to continue...{RESET}")
        except (KeyboardInterrupt, EOFError):
            return

    def _display_results_paged(self, items: List[Dict[str, Any]], title: str = "Results", page_size: int = 15) -> None:
        """Interactive table pagination with browser execution and detail view."""
        if not items:
            print(f"{YELLOW}[!] No dorks found matching criteria.{RESET}")
            input(f"{CYAN}Press Enter to continue...{RESET}")
            return

        current_page = 0
        total_pages = (len(items) + page_size - 1) // page_size

        while True:
            Utils.clear_screen()
            start = current_page * page_size
            end = min(start + page_size, len(items))
            slice_items = items[start:end]

            rows = [
                [
                    start + i + 1,
                    item.get("dork", "")[:45],
                    item.get("category", "")[:20],
                    item.get("date", ""),
                ]
                for i, item in enumerate(slice_items)
            ]

            print(f"{GREEN}=== {title} (Page {current_page + 1} of {total_pages} | Total: {len(items)}) ==={RESET}")
            print(Utils.format_table(rows, headers=["#", "Dork Query", "Category", "Date"]))
            print(f"\n{CYAN}Commands:{RESET} [n]ext, [p]rev, [1-{len(items)}] inspect/execute, [q]uit to menu")

            try:
                cmd = input(f"{YELLOW}select > {RESET}").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if cmd in ("q", "quit", "exit"):
                break
            elif cmd in ("n", "next") and current_page < total_pages - 1:
                current_page += 1
            elif cmd in ("p", "prev") and current_page > 0:
                current_page -= 1
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(items):
                    self._inspect_dork(items[idx])

    def _inspect_dork(self, dork_item: Dict[str, Any]) -> None:
        """Inspect a single dork and provide actions (Execute in Browser/Terminal or Modify with Parameters)."""
        Utils.clear_screen()
        dork_query = dork_item.get("dork", "")
        print(f"{GREEN}=== Dork Inspection & Parameter Customizer ==={RESET}")
        print(f"{CYAN}ID      :{RESET} {dork_item.get('id', 'N/A')}")
        print(f"{CYAN}Date    :{RESET} {dork_item.get('date', 'N/A')}")
        print(f"{CYAN}Category:{RESET} {dork_item.get('category', 'N/A')}")
        print(f"{CYAN}Author  :{RESET} {dork_item.get('author', 'N/A')}")
        print(f"{YELLOW}Dork    :{RESET} {dork_query}")
        print(f"{BLUE}Title   :{RESET} {dork_item.get('url_title', '')}\n")

        print(f"{CYAN}Actions:{RESET}")
        print(f" [1] Launch in Web Browser (As-is)")
        print(f" [2] Execute Search in Terminal (As-is)")
        print(f" [3] Modify / Add Parameters & Execute (site, path, custom query)")
        print(f" [0] Return to results")

        try:
            act = input(f"\n{YELLOW}action > {RESET}").strip()
            if act == "1":
                DorkSearcher.open_in_browser(dork_query)
                input(f"\n{CYAN}Press Enter to continue...{RESET}")
            elif act == "2":
                print(f"{CYAN}[*] Executing terminal search for: {dork_query}...{RESET}")
                results = DorkSearcher.search(dork_query, num_results=10)
                if results:
                    rows = [[i, r["title"][:50], r["url"]] for i, r in enumerate(results, 1)]
                    print(f"\n{GREEN}=== Search Results ({len(results)}) ==={RESET}")
                    print(Utils.format_table(rows, headers=["#", "Title", "URL"]))
                else:
                    print(f"{YELLOW}[!] No results found or query throttled.{RESET}")
                google_url = DorkSearcher.build_google_url(dork_query)
                print(f"{CYAN}[*] Google Search URL: {RESET}{google_url}")
                input(f"\n{CYAN}Press Enter to continue...{RESET}")
            elif act == "3":
                self._modify_and_execute(dork_query)
        except (KeyboardInterrupt, EOFError):
            pass

    def _modify_and_execute(self, base_query: str) -> None:
        """Interactive workflow to edit a selected dork, add parameters, and execute via terminal or browser."""
        current_query = base_query
        while True:
            Utils.clear_screen()
            print(f"{GREEN}=== Dork Parameter Modifier & Query Executor ==={RESET}")
            print(f"{CYAN}Base Dork    :{RESET} {base_query}")
            print(f"{YELLOW}Active Query :{RESET} {current_query}\n")

            print(f"{CYAN}Query Modifications:{RESET}")
            print(f" [1] Append Target Domain / Site (e.g. site:example.com)")
            print(f" [2] Append Parameter / Keyword (e.g. filetype:pdf, inurl:admin, intext:password)")
            print(f" [3] Manually Edit Query String")
            print(f" [4] Reset to Original Query")
            print(f"\n{GREEN}Execution Targets:{RESET}")
            print(f" [T] Execute via Terminal (CLI OSINT search results)")
            print(f" [B] Execute via Web Browser (Google Search URL)")
            print(f" [0] Return / Done")

            try:
                choice = input(f"\n{YELLOW}select > {RESET}").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break

            if choice in ("0", "q", "exit", "done"):
                break
            elif choice == "1":
                domain = input(f"\n{YELLOW}Enter target domain (e.g. target.com): {RESET}").strip()
                if domain:
                    site_term = domain if domain.startswith("site:") else f"site:{domain}"
                    current_query = f"{current_query} {site_term}".strip()
                    print(f"{GREEN}[✓] Query updated: {current_query}{RESET}")
            elif choice == "2":
                param = input(f"\n{YELLOW}Enter parameter to append (e.g. inurl:admin, filetype:env): {RESET}").strip()
                if param:
                    current_query = f"{current_query} {param}".strip()
                    print(f"{GREEN}[✓] Query updated: {current_query}{RESET}")
            elif choice == "3":
                print(f"\nCurrent: {current_query}")
                edited = input(f"{YELLOW}New query: {RESET}").strip()
                if edited:
                    current_query = edited
                    print(f"{GREEN}[✓] Query updated: {current_query}{RESET}")
            elif choice == "4":
                current_query = base_query
                print(f"{GREEN}[✓] Reset to original: {current_query}{RESET}")
            elif choice in ("t", "terminal"):
                print(f"\n{CYAN}[*] Executing terminal search for: {current_query}...{RESET}")
                num_str = input(f"{YELLOW}Number of results (default: 10): {RESET}").strip()
                num = int(num_str) if num_str.isdigit() else 10
                results = DorkSearcher.search(current_query, num_results=num)
                if results:
                    rows = [[i, r["title"][:50], r["url"]] for i, r in enumerate(results, 1)]
                    print(f"\n{GREEN}=== Terminal Results for: {current_query} ({len(results)}) ==={RESET}")
                    print(Utils.format_table(rows, headers=["#", "Title", "URL"]))
                else:
                    print(f"{YELLOW}[!] No results found or query was throttled by Google.{RESET}")
                google_url = DorkSearcher.build_google_url(current_query, num=num)
                print(f"{CYAN}[*] Google Search URL: {RESET}{google_url}")
                input(f"\n{CYAN}Press Enter to return to modifier...{RESET}")
            elif choice in ("b", "browser"):
                print(f"\n{CYAN}[*] Launching Google Search in browser for: {current_query}...{RESET}")
                google_url = DorkSearcher.build_google_url(current_query)
                print(f"{CYAN}[*] Google Search URL: {RESET}{google_url}")
                DorkSearcher.open_in_browser(current_query)
                input(f"\n{CYAN}Press Enter to return to modifier...{RESET}")


# Backward compatibility aliases
DorkMasterPro = DorkMaster
