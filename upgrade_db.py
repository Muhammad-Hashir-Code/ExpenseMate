import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expensemate.db")

def upgrade():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("ALTER TABLE transactions ADD COLUMN currency TEXT DEFAULT 'USD'")
        conn.commit()
        print("Successfully added currency column.")
    except Exception as e:
        print(f"Upgrade skipped or failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
