"""
Backward compatibility wrapper for UIController.
"""
from dorkmaster.banner import display_banner, render_text_banner
from dorkmaster.core import DorkMaster

class UIController:
    """Legacy UI controller interface."""
    @staticmethod
    def display_banner():
        display_banner()

__all__ = ["UIController"]
