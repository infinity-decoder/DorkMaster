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

    GLOBAL_STYLE = questionary.Style([
        ('qmark', 'fg:#00ffff bold'),       # Cyan
        ('question', 'fg:#ffffff bold'),    # White
        ('pointer', 'fg:#ff00ff bold'),     # Magenta pointer
        ('highlighted', 'fg:#00ff00 bold'), # Green selection
        ('selected', 'fg:#00ff00'),         # Green selected
        ('text', 'fg:#ffffff'),
        ('choice-shortcut', 'fg:#ffff00 bold'), # Yellow numbers
    ])

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
        print(f"{self.COLORS['highlight']}╔══════════════════════════════════════════════════════════╗")
        print(f"║ {self.COLORS['primary']}>>> SYSTEM MAIN NAVIGATION <<<".ljust(69) + f"{self.COLORS['highlight']}║")
        print(f"╚══════════════════════════════════════════════════════════╝")
        
        choices = [
            questionary.Choice("🔍 [1] Search Intelligence Database", value="1"),
            questionary.Choice("📥 [2] Incremental Update (Newest Only)", value="2"),
            questionary.Choice("🔄 [3] Full Database Synchronization", value="3"),
            questionary.Choice("📂 [4] Browse Intelligence by Category", value="4"),
            questionary.Choice("⚡ [5] Quick Execution (Raw Dork)", value="5"),
            questionary.Choice("📊 [6] View System Statistics", value="6"),
            questionary.Choice("📤 [7] Export Intelligence (JSON/CSV)", value="7"),
            questionary.Choice("❌ [8] Terminate Session", value="8")
        ]
        
        selection = questionary.select(
            "Select operation mode:",
            choices=choices,
            use_shortcuts=True,
            style=self.GLOBAL_STYLE
        ).ask()
        
        if selection:
            return selection
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
            questionary.Choice("🚀 [1] Run Dork (Execution Hub)", value="run"),
            questionary.Choice("📝 [2] Edit Query before execution", value="edit"),
            questionary.Choice("⭐ [3] Save to Mission Favorites", value="fav"),
            questionary.Choice("🔙 [4] Return to Intel List", value="back"),
            questionary.Choice("🏠 [5] Return to Tactical Hub", value="hub")
        ]
        
        res = questionary.select(
            "Intelligence Action:",
            choices=choices,
            use_shortcuts=True,
            style=self.GLOBAL_STYLE
        ).ask()
        
        mapping = {
            "run": "Run as is", 
            "edit": "Edit before running", 
            "fav": "Save to favorites", 
            "back": "Back to results",
            "hub": "Return to Hub"
        }
        return mapping.get(res)

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
            btn_count = 1
            
            if end < total_results:
                nav_choices.append(questionary.Choice(f"➡️  [{btn_count}] Next Intel Page", value="next"))
                btn_count += 1
            
            if current_page > 0:
                nav_choices.append(questionary.Choice(f"⬅️  [{btn_count}] Previous Intel Page", value="prev"))
                btn_count += 1
            
            nav_choices.append(questionary.Choice(f"🎯 [{btn_count}] Select Intel by ID", value="select"))
            btn_count += 1
            
            nav_choices.append(questionary.Choice(f"🏠 [{btn_count}] Return to Tactical Hub", value="home"))
            
            selection = questionary.select(
                "Navigation Command:",
                choices=nav_choices,
                use_shortcuts=True,
                style=self.GLOBAL_STYLE
            ).ask()
            
            if selection == "next":
                current_page += 1
            elif selection == "prev":
                current_page -= 1
            elif selection == "select":
                dork_id_str = questionary.text("Enter ID of target intel (# from table):").ask()
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
