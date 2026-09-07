"""
Banner rendering module for DorkMaster.
Supports dynamic ANSI/ASCII terminal art from embedded PNG assets using ascii-magic,
with graceful fallback to styled text banners.
"""

import os
import sys
from pathlib import Path

# Safe ANSI colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    CYAN = Style.BRIGHT + Fore.CYAN
    GREEN = Style.BRIGHT + Fore.GREEN
    MAGENTA = Style.BRIGHT + Fore.MAGENTA
    YELLOW = Style.BRIGHT + Fore.YELLOW
    RESET = Style.RESET_ALL
except ImportError:
    CYAN = ""
    GREEN = ""
    MAGENTA = ""
    YELLOW = ""
    RESET = ""


def get_banner_image_path() -> Path | None:
    """
    Dynamically locates the bundled dorkmaster.png asset across all installation types:
    system /usr/share, virtualenv site-packages, editable mode, or direct repository clone.
    """
    # 1. Standard Python 3.9+ resource loading (wheel/site-packages/.deb)
    try:
        from importlib.resources import files
        resource_path = files("dorkmaster").joinpath("assets/dorkmaster.png")
        p = Path(str(resource_path))
        if p.is_file():
            return p
    except (ImportError, TypeError, AttributeError, OSError):
        pass

    # 2. Relative to current file package directory
    local_pkg = Path(__file__).resolve().parent / "assets" / "dorkmaster.png"
    if local_pkg.is_file():
        return local_pkg

    # 3. Project root assets folder
    root_asset = Path(__file__).resolve().parent.parent / "assets" / "dorkmaster.png"
    if root_asset.is_file():
        return root_asset

    # 4. Standard Freedesktop system installation path
    system_path = Path("/usr/share/icons/hicolor/128x128/apps/dorkmaster.png")
    if system_path.is_file():
        return system_path

    return None


def render_image_banner(columns: int = 70) -> bool:
    """
    Renders the PNG logo directly to stdout using ascii-magic.
    Returns True on success, False on failure or unsupported environment.
    """
    # Do not attempt ANSI block rendering if stdout is redirected or not a TTY
    if not sys.stdout.isatty():
        return False

    img_path = get_banner_image_path()
    if not img_path:
        return False

    try:
        from ascii_magic import AsciiArt
        art = AsciiArt.from_image(str(img_path))
        art.to_terminal(columns=columns)
        return True
    except (ImportError, AttributeError, OSError, ValueError):
        # Handle older ascii-magic or terminal sizing quirks
        try:
            import ascii_magic
            if hasattr(ascii_magic, "from_image_file"):
                ascii_magic.to_terminal(ascii_magic.from_image_file(str(img_path), columns=columns))
                return True
        except Exception:
            return False
    except Exception:
        return False

    return False


def render_text_banner(version: str = "0.0.1", author: str = "Owlopia & infinitydecoder"):
    """Renders a high-contrast Cyberpunk ANSI text banner as fallback."""
    banner_ascii = r"""
  ____             _    __  __           _            
 |  _ \  ___  _ __| | _|  \/  | __ _ ___| |_ ___ _ __ 
 | | | |/ _ \| '__| |/ / |\/| |/ _` / __| __/ _ \ '__|
 | |_| | (_) | |  |   <| |  | | (_| \__ \ ||  __/ |   
 |____/ \___/|_|  |_|\_\_|  |_|\__,_|___/\__\___|_|   
"""
    print(f"{GREEN}{banner_ascii}{RESET}")
    print(f"{MAGENTA}╔" + "═" * 58 + "╗")
    print(f"║ {CYAN}Author : {author.ljust(48)}{MAGENTA}║")
    print(f"║ {CYAN}Version: v{version.ljust(47)}{MAGENTA}║")
    print(f"║ {YELLOW}OSINT Reconnaissance & Automated Google Dorking Engine   {MAGENTA}║")
    print(f"{MAGENTA}╚" + "═" * 58 + f"╝{RESET}\n")


def display_banner(version: str = "0.0.1", author: str = "Owlopia & infinitydecoder", columns: int = 70, force_text: bool = False):
    """Unified entrypoint: tries image rendering first, falls back to text banner."""
    rendered = False
    if not force_text:
        try:
            rendered = render_image_banner(columns=columns)
        except Exception:
            rendered = False

    if not rendered:
        render_text_banner(version=version, author=author)
    else:
        # Print author badge underneath image banner
        print(f"{MAGENTA}╔" + "═" * 58 + "╗")
        print(f"║ {CYAN}DorkMaster v{version.ljust(46)}{MAGENTA}║")
        print(f"║ {CYAN}Author: {author.ljust(49)}{MAGENTA}║")
        print(f"{MAGENTA}╚" + "═" * 58 + f"╝{RESET}\n")
