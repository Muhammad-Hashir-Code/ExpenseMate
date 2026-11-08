import os
from pathlib import Path
from typing import List

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Config:
    """Externalized application configuration."""
    
    # Database configuration
    DB_PATH: str = os.getenv("EXPENSEMATE_DB_PATH", str(BASE_DIR / "expensemate.db"))
    MIGRATIONS_DIR: str = str(BASE_DIR / "src" / "data" / "migrations")
    
    # Security configuration
    PBKDF2_ITERATIONS: int = int(os.getenv("EXPENSEMATE_HASH_ITERATIONS", "100000"))
    SALT_BYTE_LENGTH: int = 16
    
    # Financial & Currency configurations
    SUPPORTED_CURRENCIES: List[str] = ["USD", "EUR", "GBP", "PKR", "INR"]
    DEFAULT_CURRENCY: str = "USD"
    
    # Payment method configurations
    SUPPORTED_PAYMENT_METHODS: List[str] = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other"]
    DEFAULT_PAYMENT_METHOD: str = "Cash"
    
    # Budget alert configurations
    DEFAULT_ALERT_THRESHOLD: float = 0.8  # 80%
    MAX_ALERT_THRESHOLD: float = 1.0     # 100%
    
    # UI configuration
    APP_TITLE: str = "ExpenseMate - Personal Expense Manager"
    WINDOW_GEOMETRY: str = "1000x700"
    MIN_WINDOW_SIZE: tuple = (800, 600)
    APPEARANCE_MODE: str = "Dark"
    COLOR_THEME: str = "dark-blue"

