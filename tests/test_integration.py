import os
import sqlite3
import pytest
from src.data import database
from src.data.database import init_db
from src.controllers.auth_controller import AuthController
from src.controllers.transaction_controller import TransactionController
from src.controllers.budget_controller import BudgetController
from src.data.migrations.migration_manager import MigrationManager


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    import gc
    db_file = tmp_path / "test_integration.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    init_db(str(db_file))
    yield
    gc.collect()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except PermissionError:
            pass


def test_it01_user_authentication_lifecycle():
    """
    IT-01: End-to-End User Registration & Authentication Workflow.
    Verifies Controller -> AuthService -> UserRepository -> SQLite Database.
    """
    auth_ctrl = AuthController()

    # 1. Register new user
    reg_res = auth_ctrl.register("hashir_student", "SecurePass2026!")
    assert reg_res.is_success
    user = reg_res.data
    assert user.id is not None
    assert user.username == "hashir_student"

    # 2. Prevent duplicate user registration
    dup_res = auth_ctrl.register("hashir_student", "AnotherPassword!")
    assert not dup_res.is_success
    assert "already exists" in dup_res.error_message

    # 3. Test successful authentication
    login_res = auth_ctrl.login("hashir_student", "SecurePass2026!")
    assert login_res.is_success
    assert login_res.data.id == user.id

    # 4. Test failed authentication with invalid password
    bad_login_res = auth_ctrl.login("hashir_student", "WrongPassword123")
    assert not bad_login_res.is_success
    assert "Invalid username or password" in bad_login_res.error_message


def test_it02_multicurrency_transaction_ingestion():
    """
    IT-02: Multi-Currency & Payment Method Transaction Ingestion.
    Verifies Controller -> TransactionService -> TransactionRepository -> SQLite Database.
    """
    auth_ctrl = AuthController()
    tx_ctrl = TransactionController()

    user = auth_ctrl.register("currency_user", "pass123").data

    # Add USD expense with Credit Card
    res1 = tx_ctrl.create_transaction(
        user_id=user.id,
        t_type="expense",
        amount_input="120.00",
        date_input="2026-10-10",
        category="Tech",
        description="USB Hub",
        currency="USD",
        payment_method="Credit Card",
        tags="hardware,accessories",
    )
    assert res1.is_success

    # Add EUR income with Bank Transfer
    res2 = tx_ctrl.create_transaction(
        user_id=user.id,
        t_type="income",
        amount_input="500.00",
        date_input="2026-10-12",
        category="Consulting",
        description="Client Project",
        currency="EUR",
        payment_method="Bank Transfer",
        tags="freelance",
    )
    assert res2.is_success

    # Add PKR expense with Cash
    res3 = tx_ctrl.create_transaction(
        user_id=user.id,
        t_type="expense",
        amount_input="3500.00",
        date_input="2026-10-14",
        category="Books",
        description="Course Textbook",
        currency="PKR",
        payment_method="Cash",
    )
    assert res3.is_success

    # Fetch and verify transaction history
    list_res = tx_ctrl.get_transactions(user.id)
    assert list_res.is_success
    txs = list_res.data
    assert len(txs) == 3

    # Check that payment methods and currencies are persisted correctly
    currencies = {t.currency for t in txs}
    payment_methods = {t.payment_method for t in txs}
    assert currencies == {"USD", "EUR", "PKR"}
    assert payment_methods == {"Credit Card", "Bank Transfer", "Cash"}


def test_it03_budget_threshold_alert_lifecycle():
    """
    IT-03: Budget Threshold Breach & Automated Alert Lifecycle.
    Verifies BudgetController -> BudgetService -> BudgetRepository
    and TransactionController -> TransactionService (SQL aggregation) alert evaluation.
    """
    auth_ctrl = AuthController()
    budget_ctrl = BudgetController()
    tx_ctrl = TransactionController()

    user = auth_ctrl.register("budget_student", "pass123").data

    # 1. Set budget of $500 for 'Travel', alert at 80% ($400)
    b_res = budget_ctrl.set_budget(
        user_id=user.id,
        category="Travel",
        limit_input="500.00",
        threshold_pct_input="80",
    )
    assert b_res.is_success
    assert b_res.data.monthly_limit == 500.0
    assert b_res.data.alert_threshold == 0.8

    # 2. Add expense of $250 (50% usage) -> No alert expected
    tx_res1 = tx_ctrl.create_transaction(
        user_id=user.id,
        t_type="expense",
        amount_input="250.00",
        date_input="2026-10-05",
        category="Travel",
        description="Train tickets",
    )
    assert tx_res1.is_success
    tx1, alert1 = tx_res1.data
    assert alert1 is None

    # Check budget status before threshold breach
    status1 = budget_ctrl.get_budget_status(user.id, "Travel", 250.0).data
    assert status1["is_alert"] is False
    assert status1["remaining"] == 250.0
    assert status1["usage_percentage"] == 50.0

    # 3. Add expense of $160 (Month total = 250 + 160 = $410 -> 82% usage -> Breach!)
    tx_res2 = tx_ctrl.create_transaction(
        user_id=user.id,
        t_type="expense",
        amount_input="160.00",
        date_input="2026-10-18",
        category="Travel",
        description="Hotel deposit",
    )
    assert tx_res2.is_success
    tx2, alert2 = tx_res2.data
    assert alert2 is not None
    assert "ALERT" in alert2
    assert "$410.00" in alert2
    assert "82.0%" in alert2

    # Check budget status after threshold breach
    status2 = budget_ctrl.get_budget_status(user.id, "Travel", 410.0).data
    assert status2["is_alert"] is True
    assert status2["remaining"] == 90.0


def test_it04_csv_import_tolerance_and_export(tmp_path):
    """
    IT-04: Robust CSV Processing with Fault Tolerance & Round-Trip Export.
    Verifies TransactionController -> CSVService -> TransactionRepository.
    """
    auth_ctrl = AuthController()
    tx_ctrl = TransactionController()

    user = auth_ctrl.register("csv_roundtrip_user", "pass123").data

    # Create CSV containing 3 valid transactions and 1 corrupted row
    source_csv = tmp_path / "incoming.csv"
    source_csv.write_text(
        "Type,Amount,Date,Category,Description,Currency,PaymentMethod,Tags\n"
        "income,1500.00,2026-10-01,Stipend,Monthly stipend,USD,Bank Transfer,uni\n"
        "expense,CORRUPT_NUM,2026-10-02,Food,Corrupt row,USD,Cash,\n"
        "expense,85.50,2026-10-03,Food,Grocery run,USD,Debit Card,groceries\n"
        "expense,40.00,2026-10-04,Transport,Bus pass,USD,Cash,travel\n",
        encoding="utf-8"
    )

    # 1. Import CSV
    import_res = tx_ctrl.import_csv(user.id, str(source_csv))
    assert import_res.is_success
    summary = import_res.data
    assert summary.total_rows == 4
    assert summary.imported_count == 3
    assert summary.skipped_count == 1
    assert summary.errors[0]["line"] == 3

    # 2. Verify imported records exist in database
    tx_list = tx_ctrl.get_transactions(user.id).data
    assert len(tx_list) == 3

    # 3. Export back to a new CSV file
    export_csv = tmp_path / "exported.csv"
    export_res = tx_ctrl.export_csv(user.id, str(export_csv))
    assert export_res.is_success
    assert export_res.data == 3

    # 4. Verify exported file exists and contains valid headers and values
    assert os.path.exists(export_csv)
    with open(export_csv, "r", encoding="utf-8") as f:
        exported_text = f.read()
    assert "Stipend" in exported_text
    assert "Grocery run" in exported_text
    assert "Bus pass" in exported_text


def test_it05_database_schema_migration_regression(tmp_path):
    """
    IT-05: Database Schema Migration & System Data Regression.
    Verifies migrating a legacy Assignment 01 database and running full Controller operations on it.
    """
    legacy_db_file = tmp_path / "legacy_regression.db"
    conn = sqlite3.connect(str(legacy_db_file))

    # Construct old schema from Assignment 01
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

    # Populate legacy records
    conn.execute("INSERT INTO users (username, password_hash) VALUES ('legacy_hashir', 'salt123:hash123')")
    conn.execute("""
        INSERT INTO transactions (user_id, type, amount, date, category, description, currency)
        VALUES (1, 'expense', 75.00, '2026-09-01', 'Supplies', 'Notebooks', 'USD')
    """)
    conn.commit()
    conn.close()

    # Apply Migration Engine
    manager = MigrationManager(db_path=str(legacy_db_file))
    applied = manager.run_migrations()
    assert "002_add_payment_methods_and_tags" in applied

    # Point system to migrated database
    import src.data.database as db_mod
    original_db = db_mod.DB_PATH
    db_mod.DB_PATH = str(legacy_db_file)

    try:
        tx_ctrl = TransactionController()

        # Check that legacy transaction is readable and has default payment_method 'Cash'
        legacy_txs = tx_ctrl.get_transactions(1).data
        assert len(legacy_txs) == 1
        assert legacy_txs[0].description == "Notebooks"
        assert legacy_txs[0].payment_method == "Cash"

        # Now add a new transaction using new features (payment method and tags)
        new_tx_res = tx_ctrl.create_transaction(
            user_id=1,
            t_type="income",
            amount_input="1000.00",
            date_input="2026-10-01",
            category="Salary",
            payment_method="Bank Transfer",
            tags="monthly,job",
        )
        assert new_tx_res.is_success

        # Check total count is now 2
        all_txs = tx_ctrl.get_transactions(1).data
        assert len(all_txs) == 2
    finally:
        db_mod.DB_PATH = original_db

