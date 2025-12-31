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
        self.ui.display_message("Initializing search...", "info")
        self.ui.display_message(f"Dork: {dork_text}", "highlight")
        self.ui.display_message("Warning: Unauthorized testing is illegal. Use responsibly.", "warning")
        
        results = []
        try:
            # googlesearch-python usage: search(query, num_results, lang, sleep_interval)
            # Some versions use 'advanced=True' to get snippets/titles
            # We'll use a basic search and try to present it cleanly.
            
            search_gen = search(
                dork_text, 
                num=num_results, 
                stop=num_results, 
                pause=sleep_interval,
                user_agent=random.choice(self.USER_AGENTS)
            )
            
            print(f"\n{Fore.GREEN}[+] FETCHING RESULTS...")
            count = 0
            for url in search_gen:
                count += 1
                results.append(url)
                print(f"{Fore.CYAN}[{count}] {url}")
                # We can't easily get titles/snippets with the basic search generator
                # without extra requests, but we'll stick to URLs for now as per plan
                # to avoid excessive blocking.
            
            if not results:
                self.ui.display_message("No results found or Google blocked the request.", "warning")
            
            return results

        except Exception as e:
            self.ui.display_message(f"Search Error: {e}", "error")
            return []

    def format_results_table(self, results):
        if not results:
            return "No results to display."
        
        table_data = [[i+1, url] for i, url in enumerate(results)]
        return tabulate(table_data, headers=["#", "URL"], tablefmt="grid")
