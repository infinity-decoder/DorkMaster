import os
import sys
import pyfiglet
from colorama import Fore, Style, init
import questionary
from tabulate import tabulate

init(autoreset=True)

class UIController:
    BANNER_FONT = "slant"
    AUTHOR = "infinitydecoder"
    VERSION = "1.0"

    COLORS = {
        "primary": Style.BRIGHT + Fore.CYAN,      # Vibrant Cyan
        "secondary": Style.BRIGHT + Fore.GREEN,   # Neon Green
        "warning": Style.BRIGHT + Fore.YELLOW,    # Warning Yellow
        "error": Style.BRIGHT + Fore.RED,         # Critical Red
        "info": Fore.WHITE,                       # Basic White
        "highlight": Style.BRIGHT + Fore.MAGENTA, # Deep Purple/Magenta
        "accent": Style.BRIGHT + Fore.BLUE        # Accent Blue
    }

    def __init__(self):
        pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_banner(self):
        self.clear_screen()
        banner_text = pyfiglet.figlet_format("DorkMaster Pro", font=self.BANNER_FONT)
        print(f"{self.COLORS['secondary']}{banner_text}")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['primary']}Author: {self.AUTHOR} | Version: {self.VERSION}".ljust(61) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}╚" + "═" * 58 + "╝\n")

    def main_menu(self):
        self.display_banner()
        print(f"{self.COLORS['primary']}--- MAIN NAVIGATION ---")
        choices = [
            "[1] Search Dorks",
            "[2] Incremental Update (Newest Only)",
            "[3] Full Database Synchronization",
            "[4] Browse by Category",
            "[5] Quick Search (Raw Dork)",
            "[6] Database Statistics",
            "[7] Export Dorks (JSON/CSV)",
            "[8] Exit"
        ]
        
        # We'll use a standard prompt that allows both arrow selection AND numeric input
        selection = questionary.select(
            "Select action (or press 1-8):",
            choices=choices,
            use_shortcuts=True, # This enables numeric shortcuts for the first 9 choices!
            style=questionary.Style([
                ('qmark', 'fg:#00ffff bold'),
                ('question', 'fg:#ffffff bold'),
                ('pointer', 'fg:#00ff00 bold'),
                ('highlighted', 'fg:#00ff00 bold'),
                ('selected', 'fg:#00ff00'),
            ])
        ).ask()
        
        if selection:
            return selection.split("]")[0].strip("[")
        return None

    def display_message(self, message, msg_type="info"):
        color = self.COLORS.get(msg_type, Fore.WHITE)
        prefix = {
            "info": "[*]",
            "secondary": "[+]",
            "warning": "[!]",
            "error": "[-]",
            "highlight": "[?]"
        }.get(msg_type, "[*]")
        
        print(f"{color}{prefix} {message}")

    def show_dork_details(self, dork_id, title, dork_text, category, date, url):
        self.display_banner()
        print(f"{self.COLORS['highlight']}╔" + "═" * 60 + "╗")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['info']}DORK INTEL REPORT".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}╠" + "═" * 60 + "╣")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['accent']}ID      : {self.COLORS['info']}{dork_id}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['secondary']}Title   : {self.COLORS['info']}{title[:50]}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['secondary']}Category: {self.COLORS['info']}{category[:50]}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['primary']}Dork    : {self.COLORS['highlight']}{dork_text[:50]}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['accent']}Date    : {self.COLORS['info']}{date}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}║ {self.COLORS['accent']}Source  : {self.COLORS['info']}{url[:50]}".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"{self.COLORS['highlight']}╚" + "═" * 60 + "╝")
        
        choices = [
            "Run as is",
            "Edit before running",
            "Save to favorites",
            "Back to results"
        ]
        
        return questionary.select("Manage Dork:", choices=choices).ask()

    def paginate_results(self, results, page_size=10, title="Search Results", start_page=0):
        total_results = len(results)
        if total_results == 0:
            self.display_message("No results found.", "warning")
            input("\nPress Enter to return...")
            return None, 0

        current_page = start_page
        while True:
            self.clear_screen()
            self.display_banner()
            
            start = current_page * page_size
            end = min(start + page_size, total_results)
            
            table_data = []
            for i in range(start, end):
                # results: list of (id, title, dork_text, category)
                r = results[i]
                table_data.append([i + 1, r[1], r[2][:50] + "..." if len(r[2]) > 50 else r[2]])

            print(f"{self.COLORS['primary']}{title} (Page {current_page + 1}/{(total_results + page_size - 1) // page_size})")
            print(tabulate(table_data, headers=["#", "Title", "Dork"], tablefmt="grid"))
            
            nav_choices = []
            if end < total_results:
                nav_choices.append("Next Page")
            if current_page > 0:
                nav_choices.append("Previous Page")
            
            nav_choices.extend(["Select Dork by ID", "Back to Menu"])
            
            selection = questionary.select("Navigation:", choices=nav_choices).ask()
            
            if selection == "Next Page":
                current_page += 1
            elif selection == "Previous Page":
                current_page -= 1
            elif selection == "Select Dork by ID":
                dork_id_str = questionary.text("Enter ID number (# from table):").ask()
                try:
                    idx = int(dork_id_str) - 1
                    if 0 <= idx < total_results:
                        return results[idx], current_page
                    else:
                        self.display_message("Invalid ID.", "error")
                except ValueError:
                    self.display_message("Please enter a number.", "error")
            else:
                return None, current_page

    def edit_dork_prompt(self, original_text):
        self.display_message("Editing Dork (use backspace/arrows and press Enter to save)", "warning")
        new_text = questionary.text(
            "Modify Dork:",
            default=original_text
        ).ask()
        return new_text if new_text and new_text.strip() else None
