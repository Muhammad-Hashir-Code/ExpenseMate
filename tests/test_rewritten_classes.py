import os
import pytest
from src.data import database
from src.data.database import init_db
from src.services.auth_service import AuthService
from src.services.budget_service import BudgetService
from src.services.transaction_service import TransactionService
from src.services.csv_service import CSVService, ImportResult


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    import gc
    db_file = tmp_path / "test_rewritten.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    init_db(str(db_file))
    yield
    gc.collect()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except PermissionError:
            pass


def test_rewritten_transaction_service_sql_aggregation():
    auth = AuthService()
    budget_svc = BudgetService()
    tx_svc = TransactionService()

    user = auth.register("sql_test_user", "pass123")

    # Set budget of $200 with 75% threshold ($150) for 'Entertainment'
    budget_svc.set_budget(user.id, "Entertainment", 200.0, 0.75)

    # Add expense in September 2026 ($100) -> No alert
    tx1, alert1 = tx_svc.add_transaction(
        user.id, "expense", 100.0, "2026-09-10", "Entertainment"
    )
    assert alert1 is None

    # Add expense in August 2026 ($100) -> Different month! Should NOT trigger alert for Sept
    tx_old, alert_old = tx_svc.add_transaction(
        user.id, "expense", 100.0, "2026-08-15", "Entertainment"
    )
    assert alert_old is None

    # Add expense in September 2026 for different category ($100) -> Should NOT trigger Entertainment alert
    tx_other, alert_other = tx_svc.add_transaction(
        user.id, "expense", 100.0, "2026-09-12", "Dining"
    )
    assert alert_other is None

    # Add expense in September 2026 for Entertainment ($60) -> Sept Total = 100 + 60 = 160 > 150 -> ALERT!
    tx2, alert2 = tx_svc.add_transaction(
        user.id, "expense", 60.0, "2026-09-20", "Entertainment"
    )
    assert alert2 is not None
    assert "ALERT" in alert2
    assert "$160.00" in alert2

    # Financial Summary check
    summary = tx_svc.get_dashboard_summary(user.id)
    assert summary["expense"] == 360.0
    assert summary["income"] == 0.0

    # Category breakdown check
    breakdown = tx_svc.get_category_breakdown(user.id)
    assert breakdown["Entertainment"] == 260.0
    assert breakdown["Dining"] == 100.0


def test_rewritten_csv_service_header_validation(tmp_path):
    auth = AuthService()
    csv_svc = CSVService()
    user = auth.register("csv_test_user", "pass123")

    # Missing 'Amount' column
    bad_csv = tmp_path / "missing_header.csv"
    bad_csv.write_text("Type,Date,Category\nexpense,2026-10-01,Food\n", encoding="utf-8")

    res: ImportResult = csv_svc.import_transactions_detailed(user.id, str(bad_csv))
    assert not res.is_success
    assert res.imported_count == 0
    assert any("Missing required headers" in e["error"] for e in res.errors)


def test_rewritten_csv_service_malformed_rows_recovery(tmp_path):
    auth = AuthService()
    csv_svc = CSVService()
    user = auth.register("csv_user_robust", "pass123")

    # CSV with 1 valid row, 1 bad date, 1 bad amount, 1 valid row
    mixed_csv = tmp_path / "mixed.csv"
    content = (
        "Type,Amount,Date,Category,Description,Currency,PaymentMethod,Tags\n"
        "expense,50.00,2026-10-01,Groceries,Good row,USD,Cash,food\n"
        "expense,INVALID_AMOUNT,2026-10-02,Groceries,Bad amount row,USD,Cash,\n"
        "expense,30.00,INVALID_DATE,Groceries,Bad date row,USD,Cash,\n"
        "income,200.00,2026-10-04,Freelance,Another good row,USD,Bank Transfer,salary\n"
    )
    mixed_csv.write_text(content, encoding="utf-8")

    # Test Non-Atomic import (skips bad rows, keeps valid rows, logs errors)
    result = csv_svc.import_transactions_detailed(user.id, str(mixed_csv), atomic=False)
    assert result.total_rows == 4
    assert result.imported_count == 2
    assert result.skipped_count == 2
    assert len(result.errors) == 2
    assert result.errors[0]["line"] == 3
    assert "Invalid numeric amount" in result.errors[0]["error"]
    assert result.errors[1]["line"] == 4
    assert "Invalid date" in result.errors[1]["error"]

    # Test Atomic import on the same file (should reject all rows because errors exist)
    user2 = auth.register("csv_user_atomic", "pass123")
    atomic_result = csv_svc.import_transactions_detailed(user2.id, str(mixed_csv), atomic=True)
    assert atomic_result.imported_count == 0
    assert atomic_result.skipped_count == 2

