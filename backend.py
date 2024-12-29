import sqlite3

# Function to initialize the database
def init_db():
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_income REAL NOT NULL,
            expenses REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Function to save budget data to the database
def save_budget_data(total_income, expenses):
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO budget (total_income, expenses) VALUES (?, ?)", (total_income, expenses))
    conn.commit()
    conn.close()

# Function to retrieve the latest budget data from the database
def get_latest_budget_data():
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_income, expenses FROM budget ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0)