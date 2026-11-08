import sqlite3
from src.core.config import Config
from src.data.migrations.migration_manager import MigrationManager

DB_PATH = Config.DB_PATH


def get_connection(db_path: str = None) -> sqlite3.Connection:
    """Returns a new SQLite database connection with row_factory and foreign keys enabled."""
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str = None):
    """Initializes the database schema using versioned migrations."""
    target_path = db_path or DB_PATH
    manager = MigrationManager(db_path=target_path)
    manager.run_migrations()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized successfully at {DB_PATH}.")
