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
            "length": 250, # Larger chunks for full sync
            "search[value]": "",
            "search[regex]": "false"
        }

        new_total = 0
        
        try:
            response = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=20)
            if response.status_code != 200:
                print(f"\n[!] Error: Exploit-DB returned status {response.status_code}")
                return 0
                
            data = response.json()
            records_total = data.get("recordsTotal", 0)
            
            if records_total == 0:
                print("\n[!] No records found. Possible API change or block.")
                return 0

            print(f"[*] Found {records_total} dorks. Starting full synchronization...")
            pbar = tqdm(total=records_total, desc="[+] Syncing GHDB", unit="dork")
            
            start = 0
            # To avoid saving 7000+ times, we'll save every few batches
            batch_save_counter = 0

            while start < records_total:
                params["start"] = start
                try:
                    resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=20)
                    if resp.status_code != 200:
                        print(f"\n[!] Batch failed at index {start}")
                        break
                        
                    dorks_list = resp.json().get("data", [])
                    if not dorks_list: break
                    
                    for item in dorks_list:
                        # Safer extraction
                        html = item.get("url_title", "")
                        dork_text = html.split(">")[1].split("<")[0] if ">" in html and "<" in html else html
                        
                        added = self.data_manager.add_dork(
                            title=dork_text,
                            dork_text=dork_text,
                            category_name=item.get("category", {}).get("cat_title", "Unknown"),
                            date_published=item.get("date", ""),
                            url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                        )
                        if added: new_total += 1
                    
                    start += len(dorks_list)
                    pbar.update(len(dorks_list))
                    
                    batch_save_counter += 1
                    if batch_save_counter >= 4: # Save every 1000 dorks roughly
                        self.data_manager.save_data()
                        batch_save_counter = 0
                        
                    time.sleep(0.3) 
                except Exception as e:
                    print(f"\n[!] Error during batch {start}: {e}")
                    time.sleep(2) # Backoff
                    continue

            pbar.close()
            self.data_manager.save_data() # Final save
            self.data_manager.log_update(new_total)
            return new_total
            
        except Exception as e:
            print(f"[!] Scraper Error: {e}")
            return 0

    def update_incremental(self):
        """
        Incremental update for newest dorks.
        """
        params = {
            "draw": 1,
            "start": 0,
            "length": 100,
            "order[0][column]": 0,
            "order[0][dir]": "desc",
            "search[value]": "",
            "search[regex]": "false"
        }
        
        new_count = 0
        try:
            resp = requests.get(self.DATA_ENDPOINT, params=params, headers=self.HEADERS, timeout=15)
            if resp.status_code != 200: return 0
                
            dorks_list = resp.json().get("data", [])
            for item in dorks_list:
                html = item.get("url_title", "")
                dork_text = html.split(">")[1].split("<")[0] if ">" in html and "<" in html else html
                
                added = self.data_manager.add_dork(
                    title=dork_text,
                    dork_text=dork_text,
                    category_name=item.get("category", {}).get("cat_title", "Unknown"),
                    date_published=item.get("date", ""),
                    url=f"https://www.exploit-db.com/ghdb/{item.get('id')}"
                )
                if added: new_count += 1
                # In incremental, we don't necessarily stop at the first duplicate 
                # because GHDB pagination/sorting can be slightly jittery.
                # But if we see 20 duplicates in a row, we are likely caught up.
                # However, for 100 length, we just process all of them.
            
            if new_count > 0:
                self.data_manager.save_data()
                self.data_manager.log_update(new_count)
            return new_count
            
        except Exception as e:
            print(f"[!] Update Error: {e}")
            return 0
