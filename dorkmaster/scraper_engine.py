"""
Backward compatibility wrapper for ScraperEngine.
"""
from dorkmaster.core import DorkScraper

ScraperEngine = DorkScraper
__all__ = ["ScraperEngine", "DorkScraper"]
