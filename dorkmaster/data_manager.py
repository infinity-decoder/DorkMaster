"""
Backward compatibility wrapper for DataManager.
"""
from dorkmaster.core import DorkDatabase

DataManager = DorkDatabase
__all__ = ["DataManager", "DorkDatabase"]
