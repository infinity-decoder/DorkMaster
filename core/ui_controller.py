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
        "primary": Fore.CYAN,
        "secondary": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "info": Fore.WHITE,
        "highlight": Fore.MAGENTA
    }

    def __init__(self):
        pass

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_banner(self):
        self.clear_screen()
        banner_text = pyfiglet.figlet_format("DorkMaster Pro", font=self.BANNER_FONT)
        print(f"{self.COLORS['secondary']}{banner_text}")
        print(f"{self.COLORS['primary']}Author: {self.AUTHOR} | Version: {self.VERSION}")
        print(f"{self.COLORS['secondary']}" + "-" * 50 + "\n")

    def main_menu(self):
        choices = [
            questionary.Choice("[1] Search Dorks", value="1"),
            questionary.Choice("[2] Incremental Update (Newest Only)", value="2"),
            questionary.Choice("[3] Full Database Synchronization", value="3"),
            questionary.Choice("[4] Browse by Category", value="4"),
            questionary.Choice("[5] Quick Search (Raw Dork)", value="5"),
            questionary.Choice("[6] Database Statistics", value="6"),
            questionary.Choice("[7] Export Dorks (JSON/CSV)", value="7"),
            questionary.Choice("[8] Exit", value="8")
        ]
        return questionary.select(
            "Main Menu:",
            choices=choices,
            style=questionary.Style([
                ('qmark', 'fg:#673ab7 bold'),
                ('question', 'fg:#000000 bold'),
                ('selected', 'fg:#673ab7 bold')
            ])
        ).ask()
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
        print(f"{self.COLORS['highlight']}┌" + "─" * 60 + "┐")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['info']}[ID: {dork_id}]".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['secondary']}Title: {title}".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['secondary']}Category: {category}".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['primary']}Dork: {dork_text}".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['info']}Published: {date}".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}│ {self.COLORS['info']}Source: {url}".ljust(62) + f"{self.COLORS['highlight']}│")
        print(f"{self.COLORS['highlight']}└" + "─" * 60 + "┘")
        
        choices = [
            "Run as is",
            "Edit before running",
            "Save to favorites",
            "Back to results"
        ]
        
        return questionary.select("Manage Dork:", choices=choices).ask()

    def paginate_results(self, results, page_size=10, title="Search Results"):
        total_results = len(results)
        if total_results == 0:
            self.display_message("No results found.", "warning")
            input("\nPress Enter to return...")
            return None

        current_page = 0
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
                        return results[idx]
                    else:
                        self.display_message("Invalid ID.", "error")
                except ValueError:
                    self.display_message("Please enter a number.", "error")
            else:
                return None

    def edit_dork_prompt(self, original_text):
        print(f"\n{self.COLORS['warning']}[!] ENTER NEW DORK TEXT (Leave empty to cancel):")
        new_text = input(f"{self.COLORS['info']}> ")
        return new_text if new_text.strip() else None
