import os
import sqlite3
from typing import List, Tuple
from src.core.config import Config


class MigrationManager:
    """Manages versioned database migrations with integrity verification."""

    def __init__(self, db_path: str = None, migrations_dir: str = None):
        self.db_path = db_path or Config.DB_PATH
        self.migrations_dir = migrations_dir or Config.MIGRATIONS_DIR

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def ensure_migration_table(self, conn: sqlite3.Connection):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

    def get_applied_versions(self, conn: sqlite3.Connection) -> List[str]:
        self.ensure_migration_table(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_migrations ORDER BY version ASC")
        return [row["version"] for row in cursor.fetchall()]

    def get_migration_files(self) -> List[Tuple[str, str, str]]:
        """Returns sorted list of (version, name, filepath)."""
        if not os.path.exists(self.migrations_dir):
            return []
        
        files = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith(".sql"):
                parts = filename.split("_", 1)
                if len(parts) == 2:
                    version = parts[0]
                    name = parts[1].replace(".sql", "")
                    files.append((version, name, os.path.join(self.migrations_dir, filename)))
        return files

    def run_migrations(self) -> List[str]:
        """Applies all pending migrations in order."""
        conn = self.get_connection()
        applied = []
        try:
            self.ensure_migration_table(conn)
            applied_versions = set(self.get_applied_versions(conn))
            migration_files = self.get_migration_files()

            # Pre-check: If transactions table exists from Assignment 01, ensure 001 is recognized
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
            if cursor.fetchone() and "001" not in applied_versions:
                cursor.execute(
                    "INSERT OR IGNORE INTO schema_migrations (version, name) VALUES (?, ?)",
                    ("001", "baseline_schema")
                )
                conn.commit()
                applied_versions.add("001")

            for version, name, filepath in migration_files:
                if version not in applied_versions:
                    print(f"Applying migration {version}_{name}...")
                    with open(filepath, "r", encoding="utf-8") as f:
                        sql = f.read()

                    # Execute statements
                    cursor = conn.cursor()
                    # For safety with ALTER TABLE columns that might already exist
                    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
                    for stmt in statements:
                        try:
                            cursor.execute(stmt)
                        except sqlite3.OperationalError as e:
                            # Handle duplicate column addition gracefully
                            if "duplicate column name" in str(e).lower():
                                pass
                            else:
                                raise e

                    cursor.execute(
                        "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                        (version, name)
                    )
                    conn.commit()
                    applied.append(f"{version}_{name}")

            return applied
        finally:
            conn.close()

    def verify_migration_integrity(self) -> dict:
        """Verifies schema structure and returns verification report."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row["name"] for row in cursor.fetchall()]

            cursor.execute("PRAGMA table_info(transactions)")
            tx_cols = {col["name"]: col["type"] for col in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM transactions")
            tx_count = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM budgets")
            budget_count = cursor.fetchone()["count"]

            return {
                "tables": tables,
                "transaction_columns": tx_cols,
                "has_payment_method": "payment_method" in tx_cols,
                "has_tags": "tags" in tx_cols,
                "user_count": user_count,
                "transaction_count": tx_count,
                "budget_count": budget_count,
            }
        finally:
            conn.close()


if __name__ == "__main__":
    manager = MigrationManager()
    applied = manager.run_migrations()
    print(f"Applied migrations: {applied}")
    report = manager.verify_migration_integrity()
    print("Schema Verification Report:")
    for k, v in report.items():
        print(f"  {k}: {v}")

