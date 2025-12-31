import requests
import json
import time
from tqdm import tqdm

class ScraperEngine:
    """
    Scraper for Exploit-DB Google Hacking Database (GHDB).
    Targeting the JSON endpoint for reliability.
    """
    GHDB_URL = "https://www.exploit-db.com/google-hacking-database"
    DATA_ENDPOINT = "https://www.exploit-db.com/ghdb"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def fetch_all_dorks(self):
        """
        Fetches all dorks using the paginated endpoint. 
        Exploit-DB uses DataTables which often has a 'draw' mechanism.
        We'll try to get the full list if possible or loop through.
        """
        params = {
            "draw": 1,
            "columns[0][data]": "date",
            "columns[1][data]": "url",
            "columns[2][data]": "title",
            "columns[3][data]": "category_id",
            "columns[4][data]": "author_id",
            "order[0][column]": 0,
            "order[0][dir]": "desc",
            "start": 0,
            "length": 120, # Fetch in chunks
            "search[value]v": "",
            "search[regex]": "false"
        }

        new_dorks_count = 0
        total_found = 0
        
        try:
            # First request to get total count
            response = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            records_total = data.get("recordsTotal", 0)
            total_found = records_total
            
            print(f"[*] Found {records_total} dorks in GHDB. Starting download...")
            
            pbar = tqdm(total=records_total, desc="[+] Syncing GHDB", unit="dork")
            
            start = 0
            while start < records_total:
                params["start"] = start
                resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
                resp_data = resp.json()
                
                dorks_list = resp_data.get("data", [])
                if not dorks_list:
                    break
                
                for item in dorks_list:
                    # Item structure: {'date': '2023-12-01', 'url': '<a href="...">DORK</a>', 'title': 'Title', 'category': {'id': 1, 'category': 'Name'}, ...}
                    # We need to extract the dork text from the 'url' field which is often HTML like <a href="...">the_dork_here</a>
                    dork_html = item.get("url", "")
                    # Simple extraction since it's predictable
                    if "</a>" in dork_html:
                        dork_text = dork_html.split(">")[1].split("<")[0]
                    else:
                        dork_text = dork_html
                        
                    title = item.get("title", "No Title")
                    category_info = item.get("category", {})
                    category_name = category_info.get("category", "Unknown")
                    date_published = item.get("date", "")
                    # GHDB results usually have internal IDs, but we use dork_text as unique constraint
                    
                    added = self.db_manager.add_dork(
                        title=title,
                        dork_text=dork_text,
                        category_name=category_name,
                        date_published=date_published,
                        url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                    )
                    
                    if added:
                        new_dorks_count += 1
                
                start += len(dorks_list)
                pbar.update(len(dorks_list))
                time.sleep(0.5) # Be respectful
                
            pbar.close()
            self.db_manager.log_update(new_dorks_count)
            return new_dorks_count
            
        except Exception as e:
            print(f"[!] Scraper Error: {e}")
            return 0

    def update_incremental(self):
        """
        Similar to fetch_all, but we can stop when we hit existing dorks.
        """
        params = {
            "draw": 1,
            "start": 0,
            "length": 50,
            "order[0][column]": 0,
            "order[0][dir]": "desc"
        }
        
        new_dorks_count = 0
        try:
            resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
            resp_data = resp.json()
            dorks_list = resp_data.get("data", [])
            
            for item in dorks_list:
                dork_html = item.get("url", "")
                if "</a>" in dork_html:
                    dork_text = dork_html.split(">")[1].split("<")[0]
                else:
                    dork_text = dork_html
                
                added = self.db_manager.add_dork(
                    title=item.get("title", "No Title"),
                    dork_text=dork_text,
                    category_name=item.get("category", {}).get("category", "Unknown"),
                    date_published=item.get("date", ""),
                    url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                )
                
                if added:
                    new_dorks_count += 1
                else:
                    # If we find a dork that already exists, we can stop (assuming desc order is consistent)
                    break
            
            if new_dorks_count > 0:
                self.db_manager.log_update(new_dorks_count)
            return new_dorks_count
            
        except Exception as e:
            print(f"[!] Update Error: {e}")
            return 0
