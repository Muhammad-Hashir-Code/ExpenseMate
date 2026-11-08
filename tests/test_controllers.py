import pytest
from src.data import database
from src.data.database import init_db
from src.controllers.auth_controller import AuthController
from src.controllers.transaction_controller import TransactionController
from src.controllers.budget_controller import BudgetController


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    import gc
    import os
    db_file = tmp_path / "test_controllers.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    init_db(str(db_file))
    yield
    gc.collect()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except PermissionError:
            pass


def test_auth_controller_validation():
    controller = AuthController()

    # Empty username
    res = controller.register("", "password")
    assert not res.is_success
    assert "Username is required" in res.error_message

    # Short password
    res = controller.register("alice", "12")
    assert not res.is_success
    assert "at least 4 characters" in res.error_message

    # Successful registration
    orig_res = controller.register("alice", "secret123")
    assert orig_res.is_success
    assert orig_res.data.username == "alice"

    # Duplicate username
    dup_res = controller.register("alice", "secret123")
    assert not dup_res.is_success
    assert "already exists" in dup_res.error_message

    # Valid Login
    login_res = controller.login("alice", "secret123")
    assert login_res.is_success
    assert login_res.data.id == orig_res.data.id

    # Invalid Login
    bad_login = controller.login("alice", "wrongpassword")
    assert not bad_login.is_success


def test_transaction_controller_validation():
    auth_ctrl = AuthController()
    tx_ctrl = TransactionController()

    user = auth_ctrl.register("tx_user", "pass123").data

    # Invalid amount
    res = tx_ctrl.create_transaction(user.id, "expense", "not_a_number", "2026-10-01", "Food")
    assert not res.is_success
    assert "Invalid numeric format" in res.error_message

    # Negative amount
    res = tx_ctrl.create_transaction(user.id, "expense", "-25.0", "2026-10-01", "Food")
    assert not res.is_success
    assert "greater than zero" in res.error_message

    # Missing category
    res = tx_ctrl.create_transaction(user.id, "expense", "50.0", "2026-10-01", "")
    assert not res.is_success
    assert "Category is required" in res.error_message

    # Valid expense
    res = tx_ctrl.create_transaction(
        user.id, "expense", "45.00", "2026-10-01", "Food", description="Lunch", currency="EUR", payment_method="Credit Card"
    )
    assert res.is_success
    tx, alert = res.data
    assert tx.amount == 45.0
    assert tx.currency == "EUR"
    assert tx.payment_method == "Credit Card"

    # Fetch list
    list_res = tx_ctrl.get_transactions(user.id)
    assert list_res.is_success
    assert len(list_res.data) == 1


def test_budget_controller_validation():
    auth_ctrl = AuthController()
    budget_ctrl = BudgetController()

    user = auth_ctrl.register("b_user", "pass123").data

    # Invalid threshold
    res = budget_ctrl.set_budget(user.id, "Utilities", "300.0", "150")  # > 100%
    assert not res.is_success
    assert "between 1% and 100%" in res.error_message

    # Valid budget
    res = budget_ctrl.set_budget(user.id, "Utilities", "300.0", "80")
    assert res.is_success
    assert res.data.monthly_limit == 300.0
    assert res.data.alert_threshold == 0.8
