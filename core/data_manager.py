import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path=None):
        if file_path is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.file_path = os.path.join(root_dir, "data", "dorks.json")
        else:
            self.file_path = file_path
        
        self.data = {"dorks": [], "categories": {}, "last_update": "Never", "total_dorks": 0}
        self.dork_set = set()
        self._load_data()

    def _load_data(self):
        """Loads data from the JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                # Populate the set for fast lookup
                self.dork_set = {d["dork_text"] for d in self.data.get("dorks", [])}
            except (json.JSONDecodeError, Exception) as e:
                print(f"[!] Error loading JSON data: {e}. Starting fresh.")
                self.save_data()
        else:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self.save_data()

    def save_data(self):
        """Saves the current data to the JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[!] Error saving JSON data: {e}")

    def add_dork(self, title, dork_text, category_name, date_published=None, url=None):
        """Adds a dork if it doesn't already exist."""
        # Fast duplicate check using set
        if dork_text in self.dork_set:
            return False
        
        dork_entry = {
            "id": len(self.data["dorks"]) + 1,
            "title": title,
            "dork_text": dork_text,
            "category": category_name,
            "date_published": date_published,
            "url": url,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_favorite": False
        }
        
        self.data["dorks"].append(dork_entry)
        self.dork_set.add(dork_text)
        
        # Track categories
        if category_name not in self.data["categories"]:
            self.data["categories"][category_name] = len(self.data["categories"]) + 1
            
        self.data["total_dorks"] = len(self.data["dorks"])
        return True

    def search_dorks(self, keyword):
        """Searches dorks by keyword in title or text."""
        keyword = keyword.lower()
        results = []
        for d in self.data["dorks"]:
            if keyword in d["title"].lower() or keyword in d["dork_text"].lower():
                # Format to match original DB return style: (id, title, text, category)
                results.append((d["id"], d["title"], d["dork_text"], d["category"]))
        return results

    def get_all_categories(self):
        """Returns sorted list of (name, id) tuples."""
        return sorted([(name, cid) for name, cid in self.data["categories"].items()], key=lambda x: x[0])

    def get_dorks_by_category(self, category_name):
        """Returns dorks in a specific category."""
        results = []
        for d in self.data["dorks"]:
            if d["category"] == category_name:
                results.append((d["id"], d["title"], d["dork_text"], d["date_published"], d["url"]))
        return results

    def log_update(self, count):
        """Updates the last update timestamp and count."""
        self.data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_data()

    def get_last_update(self):
        return self.data.get("last_update", "Never")

    def get_stats(self):
        return self.data.get("total_dorks", 0), len(self.data.get("categories", {}))
