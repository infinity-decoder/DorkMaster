import csv
import json
import os
from datetime import datetime

class Utils:
    @staticmethod
    def export_to_csv(filepath, results, headers):
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(results)
            return True
        except Exception:
            return False

    @staticmethod
    def export_to_json(filepath, results, headers):
        try:
            data = [dict(zip(headers, row)) for row in results]
            with open(filepath, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception:
            return False

    @staticmethod
    def export_to_txt(filepath, results):
        try:
            with open(filepath, mode='w', encoding='utf-8') as file:
                for row in results:
                    file.write(" | ".join(map(str, row)) + "\n")
            return True
        except Exception:
            return False

    @staticmethod
    def check_connectivity():
        import requests
        try:
            requests.get("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    @staticmethod
    def get_log_path():
        path = "logs/activity.log"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @staticmethod
    def log_activity(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(Utils.get_log_path(), "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
