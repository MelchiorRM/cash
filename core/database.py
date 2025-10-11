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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE NOT NULL,
                    limit_amount REAL NOT NULL,
                    created_at TIMESTSMAP DEFAULT CURRENT_TIMESTAMP
                    )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories(
                    id INTEGER PRIMIRY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals(
                    id INTEGER PRIMIRY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    deadline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    @contextmanager
    def get_connection(self):
        """Setting database connections"""
        conn = sqlite3.connect(str(self.db_path), timeout=DB_TIMEOUT)
        conn.row_factory=sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
     
    #TRANSACTION
    
    def add_transaction(self, date: str, type_: str, category: str, amount: float, description: str = "") -> int:
        """Add a new transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, type_, category, amount, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None, 
                            category: Optional[str] = None, type_: Optional[str] = None) -> List[dict]:
        """Get transactions with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM transactions WHERE 1=1'
            params = []
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            if category:
                query += ' AND category = ?'
                params.append(category)
            if type_:
                query += ' AND type = ?'
                params.append(type_)
            
            query += ' ORDER BY date DESC'
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_transaction(self, transaction_id: int, date: str, type_: str, 
                          category: str, amount: float, description: str = ""):
        """Update an existing transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions 
                SET date = ?, type = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (date, type_, category, amount, description, transaction_id))
            conn.commit()
    
    def delete_transaction(self, transaction_id: int):
        """Delete a transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
    
    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Get income, expenses, and balance for a specific month"""
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions
                WHERE date >= ? AND date < ?
            ''', (start_date, end_date))
            
            result = cursor.fetchone()
            income = result['total_income'] or 0
            expense = result['total_expense'] or 0
            
            return {
                'income': income,
                'expense': expense,
                'balance': income - expense
            }
    
    def get_expenses_by_category(self, start_date: Optional[str] = None, 
                                 end_date: Optional[str] = None) -> List[dict]:
        """Get expenses grouped by category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'Expense'
            '''
            params = []
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            
            query += ' GROUP BY category ORDER BY total DESC'
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_spending(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> List[dict]:
        """Get daily spending for trend analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT date, SUM(amount) as total
                FROM transactions
                WHERE type = 'Expense'
            '''
            params = []
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            
            query += ' GROUP BY date ORDER BY date ASC'
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    #BUDGET
    def add_budget(self, category: str, limit_amount: float):
        """Add a new budget"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO budgets (category, limit_amount)
                VALUES (?, ?)
            ''', (category, limit_amount))
            conn.commit()
    
    def get_all_budgets(self) -> List[dict]:
        """Get all budgets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM budgets ORDER BY category')
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_budget(self, budget_id: int):
        """Delete a budget"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM budgets WHERE id = ?', (budget_id,))
            conn.commit()
    
    def get_budget_status(self, year: int, month: int) -> List[dict]:
        """Get budget usage for the current month"""
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    b.id, b.category, b.limit_amount,
                    COALESCE(SUM(t.amount), 0) as spent
                FROM budgets b
                LEFT JOIN transactions t ON b.category = t.category 
                    AND t.type = 'Expense'
                    AND t.date >= ? AND t.date < ?
                GROUP BY b.category
                ORDER BY b.category
            ''', (start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
    
    #SAVINGS OPERATIONS
    def add_savings_goal(self, name: str, target_amount: float, deadline: str) -> int:
        """Add a new savings goal"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO savings_goals (name, target_amount, current_amount, deadline)
                VALUES (?, ?, 0, ?)
            ''', (name, target_amount, deadline))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_savings_goals(self) -> List[dict]:
        """Get all savings goals"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM savings_goals ORDER BY deadline')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_savings_goal_amount(self, goal_id: int, current_amount: float):
        """Update the current amount saved for a goal"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE savings_goals 
                SET current_amount = ?
                WHERE id = ?
            ''', (current_amount, goal_id))
            conn.commit()
    
    def delete_savings_goal(self, goal_id: int):
        """Delete a savings goal"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM savings_goals WHERE id = ?', (goal_id,))
            conn.commit()
    
    #CATEGORY OPERATIONS    
    def add_custom_category(self, name: str, type_: str):
        """Add a custom category (Income or Expense)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO categories (name, type)
                VALUES (?, ?)
            ''', (name, type_))
            conn.commit()
    
    def get_custom_categories(self, type_: str) -> List[str]:
        """Get custom categories for a specific type"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name FROM categories
                WHERE type = ?
                ORDER BY name
            ''', (type_,))
            return [row['name'] for row in cursor.fetchall()]
    
    def delete_category(self, category_name: str):
        """Delete a custom category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
            conn.commit()