import time
import random
from googlesearch import search
from tabulate import tabulate
from colorama import Fore, Style

class SearchEngine:
    """
    Search engine that executes dorks using googlesearch-python.
    Includes rate limiting and result formatting.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]

    def __init__(self, ui_controller):
        self.ui = ui_controller

    def execute(self, dork_text, num_results=10, lang="en", region=None, sleep_interval=None):
        """
        Executes the dork query with anti-detection measures.
        """
        self.ui.display_message("Initializing stealth search...", "info")
        self.ui.display_message(f"Dork Query: {dork_text}", "highlight")
        
        # Determine a randomized sleep interval if none is provided
        if sleep_interval is None:
            # Random delay between 5 to 12 seconds is safer for Google
            current_delay = random.uniform(5, 12)
        else:
            current_delay = sleep_interval + random.uniform(1, 3)

        results = []
        try:
            # We use a high timeout and randomized pause to avoid 429s
            search_gen = search(
                dork_text, 
                num_results=num_results, 
                lang=lang,
                sleep_interval=current_delay,
                timeout=30
            )
            
            print(f"\n{Fore.GREEN}[+] EXTRACTING INTEL (Delay: {current_delay:.1f}s)...")
            count = 0
            for url in search_gen:
                count += 1
                results.append(url)
                print(f"{Fore.CYAN}[{count}] {url}")
                if count >= num_results:
                    break
            
            if not results:
                print(f"\n{Fore.YELLOW}[!] Zero results. Google might have served a captcha or the dork is too specific.")
            
            return results

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"\n{Fore.RED}[!] ERROR: RATE LIMITED (429)")
                print(f"{Fore.YELLOW}[*] Google has detected automated activity.")
                print(f"{Fore.CYAN}[TIP] Try switching your VPN location or wait 15-30 minutes.")
                self.ui.display_message("Rate limited by Google. Please change your IP or wait.", "error")
            elif "Max retries" in error_msg or "timed out" in error_msg:
                self.ui.display_message("Connection Timeout: Network is too slow or Google is dropping requests.", "error")
            else:
                 self.ui.display_message(f"Search failed: {e}", "error")
            return []

    def format_results_table(self, results):
        if not results:
            return "No results to display."
        
        table_data = [[i+1, url] for i, url in enumerate(results)]
        return tabulate(table_data, headers=["#", "URL"], tablefmt="grid")
