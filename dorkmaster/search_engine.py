"""
Backward compatibility wrapper for SearchEngine.
"""
from dorkmaster.core import DorkSearcher

SearchEngine = DorkSearcher
__all__ = ["SearchEngine", "DorkSearcher"]
