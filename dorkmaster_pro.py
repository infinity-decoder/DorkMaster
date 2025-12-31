import sys
import time
from core.data_manager import DataManager
from core.scraper_engine import ScraperEngine
from core.ui_controller import UIController
from core.search_engine import SearchEngine
from core.utils import Utils
import questionary
from colorama import Fore

class DorkMasterPro:
    def __init__(self):
        self.data_mgr = DataManager()
        self.ui = UIController()
        self.scraper = ScraperEngine(self.data_mgr)
        self.searcher = SearchEngine(self.ui)
        self.current_results = []

    def show_disclaimer(self):
        self.ui.clear_screen()
        print(f"{Fore.RED}[!] LEGAL DISCLAIMER")
        print(f"{Fore.WHITE}" + "="*50)
        print("This tool is for authorized security research and educational purposes only.")
        print("Unauthorized use of this tool against targets without prior consent is illegal.")
        print("The author (infinitydecoder) is not responsible for any misuse or damage.")
        print("="*50)
        
        accept = questionary.confirm("Do you accept these terms and conditions?").ask()
        if not accept:
            print(f"{Fore.RED}[-] Exiting due to disclaimer rejection.")
            sys.exit(0)

    def run(self):
        self.show_disclaimer()
        
        # Initial check/scrape if data is empty
        total_dorks, _ = self.data_mgr.get_stats()
        if total_dorks == 0:
            self.ui.display_message("Local database is empty. Performing initial scrape...", "warning")
            if Utils.check_connectivity():
                self.scraper.fetch_all_dorks()
            else:
                self.ui.display_message("No internet connectivity for initial scrape.", "error")
                sys.exit(1)

        while True:
            choice = self.ui.main_menu()
            
            if choice == "1": # Search Dorks
                keyword = questionary.text("Enter search keyword (Title/Dork):").ask()
                if keyword:
                    results = self.data_mgr.search_dorks(keyword)
                    selected = self.ui.paginate_results(results, title=f"Search Results for '{keyword}'")
                    if selected:
                        self.handle_dork_selection(selected)
            
            elif choice == "2": # Incremental Update
                total_dorks, _ = self.data_mgr.get_stats()
                self.ui.display_message(f"Current local dorks: {total_dorks}", "info")
                self.ui.display_message("Checking for newest additions...", "info")
                new_count = self.scraper.update_incremental()
                self.ui.display_message(f"Update complete. {new_count} new dorks added.", "secondary")
                input("\nPress Enter to return...")

            elif choice == "3": # Full Sync
                total_dorks, _ = self.data_mgr.get_stats()
                self.ui.display_message(f"Total local dorks: {total_dorks}", "info")
                confirm = questionary.confirm("This will fetch all 7000+ dorks. It may take a few minutes. Continue?").ask()
                if confirm:
                    new_count = self.scraper.fetch_all_dorks()
                    self.ui.display_message(f"Synchronization complete! Added {new_count} dorks.", "secondary")
                input("\nPress Enter to return...")

            elif choice == "4": # Browse by Category
                categories = self.data_mgr.get_all_categories()
                cat_choices = [f"{name}" for name, cid in categories]
                cat_choices.append("Back to Main Menu")
                
                cat_sel = questionary.select("Select Category:", choices=cat_choices).ask()
                if cat_sel != "Back to Main Menu":
                    results = self.data_mgr.get_dorks_by_category(cat_sel)
                    selected = self.ui.paginate_results(results, title=f"Dorks in {cat_sel}")
                    if selected:
                        self.handle_dork_selection(selected)

            elif choice == "5": # Quick Search (Run immediate)
                dork_text = questionary.text("Enter dork to run:").ask()
                if dork_text:
                    self.current_results = self.searcher.execute(dork_text)
                    input("\nSearch finished. Press Enter to view results...")
                    print(self.searcher.format_results_table(self.current_results))
                    input("\nPress Enter to return to menu...")

            elif choice == "6": # Show Stats
                last_update = self.data_mgr.get_last_update()
                total_dorks, total_cats = self.data_mgr.get_stats()
                self.ui.display_banner()
                print(f"{Fore.CYAN}--- System Statistics ---")
                print(f"Total Local Dorks : {total_dorks}")
                print(f"Total Categories   : {total_cats}")
                print(f"Last Synchronization: {last_update}")
                input("\nPress Enter to return...")

            elif choice == "7": # Export
                self.ui.display_message("Exporting (Mock)...", "info")
                input("\nFeature coming soon... Press Enter to return.")

            elif choice == "8": # Exit
                self.ui.display_message("Exiting DorkMaster Pro. Happy Hunting!", "secondary")
                sys.exit(0)

    def handle_dork_selection(self, dork_tuple):
        # Handle variations: search=(id, title, text, cat), browse=(id, title, text, date, url)
        d_id = dork_tuple[0]
        title = dork_tuple[1]
        text = dork_tuple[2]
        
        # Determine category and URL based on tuple length or content
        category = dork_tuple[3] if len(dork_tuple) == 4 else "Unknown"
        date = dork_tuple[3] if len(dork_tuple) > 4 else "N/A"
        url = dork_tuple[4] if len(dork_tuple) > 4 else f"https://www.exploit-db.com/ghdb/{d_id}"
        
        action = self.ui.show_dork_details(d_id, title, text, category, date, url)
        
        if action == "Run as is":
            self.current_results = self.searcher.execute(text)
            input("\nSearch finished. Press Enter to view results...")
            print(self.searcher.format_results_table(self.current_results))
            input("\nPress Enter to return...")
        
        elif action == "Edit before running":
            new_text = self.ui.edit_dork_prompt(text)
            if new_text:
                self.current_results = self.searcher.execute(new_text)
                input("\nSearch finished. Press Enter to view results...")
                print(self.searcher.format_results_table(self.current_results))
                input("\nPress Enter to return...")
        
        elif action == "Save to favorites":
            self.ui.display_message("Added to favorites (Mock).", "secondary")
            input("\nPress Enter to return...")

if __name__ == "__main__":
    app = DorkMasterPro()
    try:
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user. Exiting...")
        sys.exit(0)
