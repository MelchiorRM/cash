import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

SAMPLE_DB_PATH = Path(__file__).parent / "sample_data.db"


def create_sample_database():
    """Create a sample database with test data for development"""
    
    # Remove existing sample database if it exists
    if SAMPLE_DB_PATH.exists():
        SAMPLE_DB_PATH.unlink()
        print(f"Removed existing sample database")
    
    conn = sqlite3.connect(str(SAMPLE_DB_PATH))
    cursor = conn.cursor()
    
    # Create tables with same structure as main database
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0,
                    deadline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    # Insert sample transactions (last 90 days)
    expense_data = [
        ("Food", [40, 50, 60, 45, 75]),
        ("Transportation", [15, 20, 30, 25]),
        ("Entertainment", [20, 30, 50, 25]),
        ("Bills", [150, 180, 160]),
        ("Healthcare", [50, 100, 60]),
        ("Education", [200, 300]),
        ("Other", [15, 20, 25]),
    ]
    
    income_data = [
        ("Scholarship", [50000]),
        ("Other", [500, 800, 1200]),
    ]
    
    print("Generating sample transactions...")
    
    # Generate daily transactions for 90 days
    for i in range(90):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Add expenses (multiple per day)
        for category, amounts in expense_data:
            if random.random() > 0.6:
                amount = random.choice(amounts)
                cursor.execute(
                    'INSERT INTO transactions (date, type, category, amount) VALUES (?, ?, ?, ?)',
                    (date, "Expense", category, amount)
                )
        
        # Add income occasionally
        if random.random() > 0.95:
            category, amounts = random.choice(income_data)
            amount = random.choice(amounts)
            cursor.execute(
                    'INSERT INTO transactions (date, type, category, amount) VALUES (?, ?, ?, ?)',
                    (date, "Income", category, amount)
                )
    
    # Insert sample budgets
    print("Adding sample budgets...")
    budget_data = [
        ("Food", 2000),
        ("Transportation", 1500),
        ("Other", 2000),
        ("Entertainment", 1000),
        ("Bills", 5000),
        ("Healthcare", 1500),
        ("Education", 3000),
    ]
    
    for category, limit_amount in budget_data:
        cursor.execute(
            'INSERT INTO budgets VALUES (NULL, ?, ?, CURRENT_TIMESTAMP)',
            (category, limit_amount)
        )
    
    # Insert sample savings goals
    print("Adding sample savings goals...")
    savings_data = [
        ("Emergency Fund", 100000, 35000, (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")),
        ("Vacation", 20000, 8000, (datetime.now() + timedelta(days=150)).strftime("%Y-%m-%d")),
        ("New Laptop", 30000, 5000, (datetime.now() + timedelta(days=200)).strftime("%Y-%m-%d")),
        ("Home Improvement", 50000, 15000, (datetime.now() + timedelta(days=300)).strftime("%Y-%m-%d")),
    ]
    
    for name, target, current, deadline in savings_data:
        cursor.execute(
            'INSERT INTO savings_goals VALUES (NULL, ?, ?, ?, ?, CURRENT_TIMESTAMP)',
            (name, target, current, deadline)
        )
    
    conn.commit()
    conn.close()
    
    print(f"✓ Sample database created successfully at: {SAMPLE_DB_PATH}")
    print(f"✓ Total transactions generated: ~{90 * 3}")
    print(f"✓ Budgets: {len(budget_data)}")
    print(f"✓ Savings goals: {len(savings_data)}")


if __name__ == "__main__":
    create_sample_database()
    print("\n" + "="*60)
    print("To use the sample database for testing:")
    print("1. Open config.py")
    print("2. Uncomment: DATABASE_PATH = BASE_DIR / 'data' / 'sample_finance_tracker.db'")
    print("3. Comment out: DATABASE_PATH = BASE_DIR / 'finance_tracker.db'")
    print("4. Run your application")
    print("="*60)