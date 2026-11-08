import os
import sqlite3
import pytest
from src.data.migrations.migration_manager import MigrationManager


def test_fresh_migration(tmp_path):
    """Verifies that a fresh database receives all migrations in sequence."""
    db_file = tmp_path / "fresh.db"
    manager = MigrationManager(db_path=str(db_file))
    applied = manager.run_migrations()

    assert "001_baseline_schema" in applied or "002_add_payment_methods_and_tags" in applied
    report = manager.verify_migration_integrity()
    assert report["has_payment_method"] is True
    assert report["has_tags"] is True
    assert "users" in report["tables"]
    assert "transactions" in report["tables"]
    assert "budgets" in report["tables"]


def test_legacy_database_migration_preserves_records(tmp_path):
    """Verifies that migrating an existing Assignment 01 database preserves data integrity."""
    db_file = tmp_path / "legacy.db"
    conn = sqlite3.connect(str(db_file))

    # Create pre-migration Assignment 01 schema (no payment_method, no tags, no schema_migrations)
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            currency TEXT DEFAULT 'USD'
        )
    """)
    conn.execute("""
        CREATE TABLE budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            alert_threshold REAL NOT NULL
        )
    """)

    # Insert legacy records
    conn.execute("INSERT INTO users (username, password_hash) VALUES ('legacy_user', 'hash123')")
    conn.execute("""
        INSERT INTO transactions (user_id, type, amount, date, category, description, currency)
        VALUES (1, 'expense', 45.50, '2026-09-15', 'Groceries', 'Weekly milk & eggs', 'USD')
    """)
    conn.execute("""
        INSERT INTO budgets (user_id, category, monthly_limit, alert_threshold)
        VALUES (1, 'Groceries', 200.0, 0.8)
    """)
    conn.commit()
    conn.close()

    # Now execute MigrationManager on legacy database
    manager = MigrationManager(db_path=str(db_file))
    applied = manager.run_migrations()
    assert "002_add_payment_methods_and_tags" in applied

    # Verify that existing records were preserved intact
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions WHERE id = 1")
    row = cursor.fetchone()
    assert row["amount"] == 45.50
    assert row["category"] == "Groceries"
    assert row["description"] == "Weekly milk & eggs"
    assert row["payment_method"] == "Cash"  # Default applied
    assert row["tags"] == ""

    cursor.execute("SELECT * FROM users WHERE id = 1")
    user_row = cursor.fetchone()
    assert user_row["username"] == "legacy_user"

    conn.close()

