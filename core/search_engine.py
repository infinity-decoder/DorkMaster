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

    def execute(self, dork_text, num_results=10, lang="en", region=None, sleep_interval=2):
        """
        Executes the dork query.
        """
        self.ui.display_message("Initializing high-res search...", "info")
        self.ui.display_message(f"Dork Query: {dork_text}", "highlight")
        self.ui.display_message("Ethical Warning: Unauthorized testing is strictly prohibited.", "warning")
        
        results = []
        try:
            # googlesearch-python 1.2.3: search(term, num_results=10, lang="en", timeout=10, ...)
            # We'll set a high timeout (30 seconds) to avoid connection drops.
            search_gen = search(
                dork_text, 
                num_results=num_results, 
                lang=lang,
                sleep_interval=sleep_interval,
                timeout=30 # Increased from default 5-10s
            )
            
            print(f"\n{Fore.GREEN}[+] FETCHING INTEL FROM GOOGLE...")
            count = 0
            for url in search_gen:
                count += 1
                results.append(url)
                print(f"{Fore.CYAN}[{count}] {url}")
                if count >= num_results:
                    break
            
            if not results:
                print(f"\n{Fore.YELLOW}[!] Zero results returned. This could be due to a strict dork or WAF blocking.")
            
            return results

        except Exception as e:
            # Catch common network errors and provide better context
            error_msg = str(e)
            if "Max retries exceeded" in error_msg or "timed out" in error_msg:
                self.ui.display_message("Connection Timeout: Google is either blocking us or the network is too slow.", "error")
            else:
                self.ui.display_message(f"Search Execution Failed: {e}", "error")
            return []

    def format_results_table(self, results):
        if not results:
            return "No results to display."
        
        table_data = [[i+1, url] for i, url in enumerate(results)]
        return tabulate(table_data, headers=["#", "URL"], tablefmt="grid")
