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
    # The /ghdb endpoint is broken (404), we must use the main page URL with AJAX headers
    DATA_ENDPOINT = "https://www.exploit-db.com/google-hacking-database"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.exploit-db.com/google-hacking-database"
    }

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def fetch_all_dorks(self):
        """
        Fetches all dorks using the AJAX endpoint identified via browser analysis.
        """
        params = {
            "draw": 1,
            "columns[0][data]": "date",
            "columns[1][data]": "url_title",
            "columns[2][data]": "cat_id",
            "columns[3][data]": "author_id",
            "order[0][column]": 0,
            "order[0][dir]": "desc",
            "start": 0,
            "length": 120, 
            "search[value]": "",
            "search[regex]": "false"
        }

        new_dorks_count = 0
        
        try:
            # First request to get total count
            response = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
            
            if response.status_code != 200:
                print(f"[!] GHDB returned status {response.status_code}. Using fallback or exiting.")
                return 0
                
            data = response.json()
            records_total = data.get("recordsTotal", 0)
            
            if records_total == 0:
                print("[!] No records found. Check if X-Requested-With is blocked.")
                return 0

            print(f"[*] Found {records_total} dorks in GHDB. Starting download...")
            
            pbar = tqdm(total=records_total, desc="[+] Syncing GHDB", unit="dork")
            
            start = 0
            while start < records_total:
                params["start"] = start
                resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
                
                if resp.status_code != 200:
                    break
                    
                resp_data = resp.json()
                dorks_list = resp_data.get("data", [])
                
                if not dorks_list:
                    break
                
                for item in dorks_list:
                    # Item structure: {'date': '...', 'url_title': '<a href="...">DORK</a>', 'category': {'cat_title': '...'}}
                    url_title_html = item.get("url_title", "")
                    
                    # Extract dork text from <a> tag
                    if "</a>" in url_title_html:
                        dork_text = url_title_html.split(">")[1].split("<")[0]
                    else:
                        dork_text = url_title_html
                        
                    title = dork_text # GHDB JSON returns dork text in url_title usually
                    category_info = item.get("category", {})
                    category_name = category_info.get("cat_title", "Unknown")
                    date_published = item.get("date", "")
                    
                    added = self.data_manager.add_dork(
                        title=title,
                        dork_text=dork_text,
                        category_name=category_name,
                        date_published=date_published,
                        url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                    )
                    
                    if added:
                        new_dorks_count += 1
                
                self.data_manager.save_data() # Save in chunks
                start += len(dorks_list)
                pbar.update(len(dorks_list))
                time.sleep(0.5) 
                
            pbar.close()
            self.data_manager.log_update(new_dorks_count)
            return new_dorks_count
            
        except Exception as e:
            print(f"[!] Scraper Error: {e}")
            return 0

    def update_incremental(self):
        """
        Incremental update for new dorks.
        """
        params = {
            "draw": 1,
            "start": 0,
            "length": 50,
            "order[0][column]": 0,
            "order[0][dir]": "desc",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        new_dorks_count = 0
        try:
            resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
            if resp.status_code != 200:
                return 0
                
            resp_data = resp.json()
            dorks_list = resp_data.get("data", [])
            
            for item in dorks_list:
                url_title_html = item.get("url_title", "")
                if "</a>" in url_title_html:
                    dork_text = url_title_html.split(">")[1].split("<")[0]
                else:
                    dork_text = url_title_html
                
                added = self.data_manager.add_dork(
                    title=dork_text,
                    dork_text=dork_text,
                    category_name=item.get("category", {}).get("cat_title", "Unknown"),
                    date_published=item.get("date", ""),
                    url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                )
                
                if added:
                    new_dorks_count += 1
                else:
                    break
            
            if new_dorks_count > 0:
                self.data_manager.log_update(new_dorks_count)
            return new_dorks_count
            
        except Exception as e:
            print(f"[!] Update Error: {e}")
            return 0
