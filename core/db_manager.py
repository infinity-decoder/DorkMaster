import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Get the path relative to the root of the project
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(root_dir, "data", "dorks.db")
        else:
            self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        """Initializes the database schema if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            
            # Dorks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dorks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    dork_text TEXT UNIQUE NOT NULL,
                    category_id INTEGER,
                    date_published TEXT,
                    url TEXT,
                    date_added TEXT,
                    is_favorite INTEGER DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # Update log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_update TEXT,
                    new_dorks_count INTEGER
                )
            ''')
            
            # Dork history / modification table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dork_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_dork_id INTEGER,
                    modified_text TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (original_dork_id) REFERENCES dorks (id)
                )
            ''')
            
            conn.commit()

    def add_category(self, name, description=""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', (name, description))
            conn.commit()
            cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
            return cursor.fetchone()[0]

    def add_dork(self, title, dork_text, category_name, date_published=None, url=None):
        category_id = self.add_category(category_name)
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO dorks (title, dork_text, category_id, date_published, url, date_added)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, dork_text, category_id, date_published, url, date_added))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Dork already exists
                return False

    def get_all_categories(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, id FROM categories ORDER BY name')
            return cursor.fetchall()

    def get_dorks_by_category(self, category_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.id, d.title, d.dork_text, d.date_published, d.url 
                FROM dorks d
                WHERE d.category_id = ?
            ''', (category_id,))
            return cursor.fetchall()

    def search_dorks(self, keyword, search_type="both"):
        """
        search_type: 'title', 'text', or 'both'
        """
        query = "SELECT d.id, d.title, d.dork_text, c.name FROM dorks d JOIN categories c ON d.category_id = c.id WHERE "
        params = []
        
        if search_type == "title":
            query += "d.title LIKE ?"
            params.append(f"%{keyword}%")
        elif search_type == "text":
            query += "d.dork_text LIKE ?"
            params.append(f"%{keyword}%")
        else:
            query += "(d.title LIKE ? OR d.dork_text LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def log_update(self, count):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO update_log (last_update, new_dorks_count) VALUES (?, ?)', 
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count))
            conn.commit()

    def get_last_update(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT last_update FROM update_log ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result else "Never"

    def get_stats(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM dorks')
            total_dorks = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM categories')
            total_categories = cursor.fetchone()[0]
            return total_dorks, total_categories
