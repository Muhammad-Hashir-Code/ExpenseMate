import pytest
from src.data import database
from src.data.database import init_db
from src.logic.services import AuthService, TransactionService, BudgetService, CSVService
import os

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    # Use a temporary database file for isolation
    db_file = tmp_path / "test_expensemate.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    init_db()
    yield
    if os.path.exists(db_file):
        os.remove(db_file)

def test_auth_service():
    # Test Registration
    user = AuthService.register("testuser", "password123")
    assert user.id is not None
    assert user.username == "testuser"
    
    # Test duplicate registration
    with pytest.raises(ValueError):
        AuthService.register("testuser", "anotherpassword")
        
    # Test Login
    logged_in = AuthService.login("testuser", "password123")
    assert logged_in is not None
    assert logged_in.username == "testuser"
    
    # Test invalid login
    bad_login = AuthService.login("testuser", "wrongpass")
    assert bad_login is None

def test_budget_and_transaction_alerts():
    user = AuthService.register("budgetuser", "pass")
    
    # Set a budget of $100 for Food, alert at 80% ($80)
    BudgetService.set_budget(user.id, "Food", 100.0, 0.8)
    
    # Add expense of $50 -> No alert expected
    t1, alert1 = TransactionService.add_transaction(user.id, "expense", 50.0, "2026-09-01", "Food")
    assert t1.amount == 50.0
    assert alert1 is None
    
    # Add expense of $40 -> Total $90 -> Exceeds $80 threshold!
    t2, alert2 = TransactionService.add_transaction(user.id, "expense", 40.0, "2026-09-02", "Food")
    assert alert2 is not None
    assert "ALERT" in alert2

def test_csv_import_export(tmp_path):
    user = AuthService.register("csvuser", "pass")
    TransactionService.add_transaction(user.id, "income", 1000.0, "2026-09-01", "Salary")
    
    csv_file = tmp_path / "export.csv"
    CSVService.export_transactions(user.id, str(csv_file))
    
    assert os.path.exists(csv_file)
    with open(csv_file, 'r') as f:
        content = f.read()
        assert "Salary" in content
        assert "1000.0" in content

    # Import to another user
    user2 = AuthService.register("csvuser2", "pass")
    imported = CSVService.import_transactions(user2.id, str(csv_file))
    assert imported == 1
    
    txs = TransactionService.get_transactions(user2.id)
    assert len(txs) == 1
    assert txs[0].category == "Salary"
