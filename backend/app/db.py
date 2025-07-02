# backend/app/db.py
import sqlite3

# Connect to SQLite database (will create file if it doesn't exist)
conn = sqlite3.connect("trades.db", check_same_thread=False)
cur = conn.cursor()
# Ensure the trades table exists
cur.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument TEXT,
    quantity REAL,
    entry_price REAL
)
""")
conn.commit()

def insert_trade(instrument: str, quantity: float, entry_price: float):
    """Insert a new approved trade into the trades table."""
    cur.execute(
        "INSERT INTO trades (instrument, quantity, entry_price) VALUES (?, ?, ?)",
        (instrument, quantity, entry_price)
    )
    conn.commit()

def get_trades():
    """Retrieve all trades (instrument, quantity, entry_price) from the DB."""
    cur.execute("SELECT instrument, quantity, entry_price FROM trades")
    return cur.fetchall()
