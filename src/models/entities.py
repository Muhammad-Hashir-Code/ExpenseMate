from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    username: str
    password_hash: str
    id: Optional[int] = None


@dataclass
class Transaction:
    user_id: int
    type: str  # 'income' or 'expense'
    amount: float
    date: str  # ISO format YYYY-MM-DD
    category: str
    description: str = (
        ""  # Represents 'source' for income or 'notes' for expense
    )
    currency: str = "USD"
    id: Optional[int] = None


@dataclass
class Budget:
    user_id: int
    category: str
    monthly_limit: float
    alert_threshold: float  # e.g., 0.8 for 80% or 1.0 for 100%
    id: Optional[int] = None
