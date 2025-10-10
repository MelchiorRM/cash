import  sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from config import DB_PATH, DB_TIMEOUT, DATE_FORMAT

class DatabaseManager:
    """Handle database operations"""
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize the database if it doesn't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
