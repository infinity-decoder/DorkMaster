"""
DorkMaster Command-Line Interface (CLI) Entrypoint.
Orchestrates headless terminal commands and interactive Cyberpunk TUI sessions.
"""

import argparse
import sys
from dorkmaster import __author__, __version__
from dorkmaster.banner import display_banner


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="dorkmaster",
        description="DorkMaster - Automated Google Dorking and OSINT Reconnaissance Tool (Kali Linux & Debian)",
        epilog="Run without arguments to enter the interactive Cyberpunk TUI dashboard.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"DorkMaster v{__version__} by {__author__}",
    )

    parser.add_argument(
        "-s",
        "--search",
        metavar="KEYWORD",
        help="Search cached Google dorks by keyword or title",
    )

    parser.add_argument(
        "-q",
        "--query",
        metavar="DORK",
        help="Directly execute a dork query against Google",
    )

    parser.add_argument(
        "-b",
        "--browser",
        action="store_true",
        help="Open search results directly in default web browser",
    )

    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=10,
        metavar="COUNT",
        help="Number of results to retrieve (default: 10)",
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="Synchronize full Exploit-DB GHDB library into local storage",
    )

    parser.add_argument(
        "--site",
        metavar="DOMAIN",
        default=None,
        help="Append target site constraint (e.g. --site example.com -> site:example.com)",
    )

    parser.add_argument(
        "-p",
        "--param",
        metavar="PARAM",
        default=None,
        help="Append custom parameter or keyword filter to query (e.g. filetype:log)",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics, last sync timestamp, and storage locations",
    )

    parser.add_argument(
        "--banner",
        action="store_true",
        help="Display the DorkMaster terminal ANSI art banner and exit",
    )

    parser.add_argument(
        "--data-path",
        metavar="PATH",
        default=None,
        help="Custom path to dorks database JSON file",
    )

    return parser.parse_args(args)


def main():
    try:
        args = parse_args()

        # Instant banner display
        if args.banner:
            display_banner(version=__version__, author=__author__)
            return 0

        # Lazy import of heavy modules to keep CLI snappy
        try:
            from dorkmaster.core import DorkDatabase, DorkMaster, DorkScraper, DorkSearcher
            from dorkmaster.utils import PathManager, Utils
        except ImportError as e:
            print(f"[-] Missing dependency: {e}", file=sys.stderr)
            print("[!] Please run: pip install -r requirements.txt or install via apt", file=sys.stderr)
            return 1

        app = DorkMaster(data_path=args.data_path)

        # 1. Sync GHDB
        if args.sync:
            display_banner(version=__version__, author=__author__)
            DorkScraper.sync_all(app.db)
            return 0

        # 2. Stats
        if args.stats:
            display_banner(version=__version__, author=__author__)
            stats = app.db.get_stats()
            rows = [
                ["Total Dorks Cached", stats["total_dorks"]],
                ["Categories Indexed", stats["categories_count"]],
                ["Database Location", stats["db_path"]],
                ["Last Synchronized", stats["last_modified"]],
                ["Log File Location", str(PathManager.get_default_log_path())],
            ]
            print(Utils.format_table(rows, headers=["Property", "Value"]))
            return 0

        # 3. Direct Google Query Execution
        if args.query:
            query = args.query
            if args.site:
                site_filter = args.site if args.site.startswith("site:") else f"site:{args.site}"
                query = f"{query} {site_filter}".strip()
            if args.param:
                query = f"{query} {args.param}".strip()

            if args.browser:
                print(f"[*] Opening '{query}' in default browser...")
                DorkSearcher.open_in_browser(query)
            else:
                display_banner(version=__version__, author=__author__)
                print(f"[*] Executing query: {query} (limit: {args.num})...")
                results = DorkSearcher.search(query, num_results=args.num)
                if not results:
                    print("[-] No results returned or rate-limited.")
                else:
                    rows = [[i, r["title"][:50], r["url"]] for i, r in enumerate(results, 1)]
                    print(Utils.format_table(rows, headers=["#", "Title", "URL"]))
                google_url = DorkSearcher.build_google_url(query, num=args.num)
                print(f"[*] Search URL: {google_url}")
            return 0

        # 4. Keyword Search in Cached Database
        if args.search:
            display_banner(version=__version__, author=__author__)
            matches = app.db.search(args.search)
            print(f"[*] Found {len(matches)} matching dorks for '{args.search}':\n")
            display_limit = min(len(matches), args.num)
            rows = [
                [i + 1, d.get("dork", "")[:50], d.get("category", "")[:20], d.get("date", "")]
                for i, d in enumerate(matches[:display_limit])
            ]
            if rows:
                print(Utils.format_table(rows, headers=["#", "Dork", "Category", "Date"]))
                if len(matches) > args.num:
                    print(f"\n[!] Displaying top {display_limit} of {len(matches)} results. Increase with -n COUNT.")
            else:
                print("[-] No matching dorks found in local database.")
                return 0

            # Interactive dork selection, parameter modification, and execution
            if sys.stdin.isatty():
                try:
                    from dorkmaster.core import RESET, YELLOW
                    prompt = f"\n{YELLOW}Select dork # to edit/execute (1-{display_limit}, or Enter to exit): {RESET}"
                    sel = input(prompt).strip()
                    if sel.isdigit():
                        idx = int(sel) - 1
                        if 0 <= idx < display_limit:
                            chosen_dork = matches[idx].get("dork", "")
                            if args.site:
                                site_filter = args.site if args.site.startswith("site:") else f"site:{args.site}"
                                chosen_dork = f"{chosen_dork} {site_filter}".strip()
                            if args.param:
                                chosen_dork = f"{chosen_dork} {args.param}".strip()
                            app._modify_and_execute(chosen_dork)
                except (KeyboardInterrupt, EOFError):
                    print("\n[*] Exiting.")
            return 0

        # 5. Default: Interactive Cyberpunk TUI Dashboard
        app.interactive_menu()
        return 0

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Exiting cleanly.")
        return 0
    except Exception as e:
        print(f"[-] Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
