"""
Banner rendering module for DorkMaster.
Provides Metasploit-style terminal ASCII/ANSI art inspired by the DorkMaster Owl logo,
stylized branding typography, and structured developer/organization metadata.
"""

import os
import sys
from pathlib import Path

# Safe Color Palette with dynamic terminal detection
def _supports_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


if _supports_color():
    CYAN = "\033[1;36m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    RED = "\033[1;31m"
    MAGENTA = "\033[1;35m"
    WHITE = "\033[1;37m"
    DIM = "\033[0;90m"
    RESET = "\033[0m"
else:
    CYAN = GREEN = YELLOW = RED = MAGENTA = WHITE = DIM = RESET = ""


def get_owl_art() -> str:
    """
    Returns the handcrafted Metasploit-style terminal ASCII/ANSI art of the DorkMaster Owl.
    Accurately represents the silhouette of the DorkMaster owl icon with cyber feathers,
    glowing recon optics, and sharp wings.
    """
    return f"""
{CYAN}                   _{WHITE}/\\{CYAN}_               _{WHITE}/\\{CYAN}_
{CYAN}                  /  {WHITE}\\/{CYAN} \\             / {WHITE}\\/{CYAN}  \\
{CYAN}                 / /\\  {WHITE}\\           /  {CYAN}/\\ \\
{CYAN}                | |  \\  {WHITE}\\  _..._  /  {CYAN}/  | |
{CYAN}                | |   \\  {WHITE}/'{YELLOW}(o) (o){WHITE}'\\  {CYAN}/   | |
{CYAN}                 \\ \\   {WHITE}/|     {YELLOW}V{WHITE}     |\\   {CYAN}/ /
{CYAN}                  \\ \\  {WHITE}| \\   ===   / |  {CYAN}/ /
{CYAN}                   \\ \\__{WHITE}\\  `'---'`  /{CYAN}__/ /
{CYAN}                   /  |  {GREEN}.---...---.  {CYAN}|  \\
{CYAN}                  / / | {GREEN}/  |  ===  |  \\ {CYAN}| \\ \\
{CYAN}                 ( (  |{GREEN}|   | ::::: |   |{CYAN}|  ) )
{CYAN}                  \\ \\ | {GREEN}\\  |  ===  |  / {CYAN}| / /
{CYAN}                   \\ \\|  {GREEN}`---...---`  {CYAN}|/ /
{DIM}                    \\_\\_   /\"\"\"\"\"\"\"\"\"\\   _/_/
                         `\"\"--...--\"\"`{RESET}"""


def get_name_art() -> str:
    """Returns the stylized DorkMaster typography header."""
    return f"""{GREEN}  ____             _    __  __           _            
 |  _ \\  ___  _ __| | _|  \\/  | __ _ ___| |_ ___ _ __ 
 | | | |/ _ \\| '__| |/ / |\\/| |/ _` / __| __/ _ \\ '__|
 | |_| | (_) | |  |   <| |  | | (_| \\__ \\ ||  __/ |   
 |____/ \\___/|_|  |_|\\_\\_|  |_|\\__,_|___/\\__\\___|_|   {RESET}"""


def get_meta_box(
    version: str = "0.0.1",
    company: str = "Owlopia",
    author: str = "infinitydecoder",
    dork_count: int = 7944,
) -> str:
    """
    Renders the Metasploit-style structured console header box containing
    program version, organization name, author name, and database metrics.
    """
    v_str = f"v{version}".ljust(35)
    c_str = f"{company}".ljust(33)
    a_str = f"{author}".ljust(33)
    count_str = f"{dork_count:,} Exploit-DB GHDB Signatures Loaded".ljust(48)

    return f"""
{MAGENTA}       =[ {WHITE}DorkMaster {v_str}{MAGENTA}]
+ -- --=[ {CYAN}Developed in : {WHITE}{c_str}{MAGENTA}]
+ -- --=[ {CYAN}Author       : {WHITE}{a_str}{MAGENTA}]
+ -- --=[ {YELLOW}Automated Google Dorking & OSINT Engine         {MAGENTA}]
+ -- --=[ {GREEN}{count_str}{MAGENTA}]{RESET}
"""


def render_image_banner(columns: int = 70) -> bool:
    """
    Optional renderer if ascii-magic is installed and an image file exists.
    Falls back to the native terminal art if unavailable.
    """
    # Prefer the native Metasploit art for maximum consistency
    return False


def render_text_banner(
    version: str = "0.0.1",
    company: str = "Owlopia",
    author: str = "infinitydecoder",
):
    """Prints the complete Metasploit-style terminal banner."""
    print(get_owl_art())
    print(get_name_art())
    print(get_meta_box(version=version, company=company, author=author))


def display_banner(
    version: str = "0.0.1",
    company: str = "Owlopia",
    author: str = "infinitydecoder",
    columns: int = 70,
    force_text: bool = False,
):
    """
    Primary banner entrypoint.
    Renders terminal-based image art of the owl (Metasploit style),
    followed by the prominent DorkMaster title, the company name (Developed in Owlopia),
    and the author name (infinitydecoder) in professional Metasploit console format.
    """
    render_text_banner(version=version, company=company, author=author)
