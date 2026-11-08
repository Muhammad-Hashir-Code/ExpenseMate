"""
Backward-compatibility facade for services.
Delegates all calls to the modernized, rewritten services in src.services.
"""
from typing import List, Optional, Tuple
from src.models.entities import User, Transaction, Budget
from src.services.auth_service import AuthService as _AuthService
from src.services.budget_service import BudgetService as _BudgetService
from src.services.transaction_service import TransactionService as _TransactionService
from src.services.csv_service import CSVService as _CSVService, ImportResult


class AuthService:
    _service = _AuthService()

    @staticmethod
    def register(username: str, password: str) -> User:
        return AuthService._service.register(username, password)

    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        return AuthService._service.login(username, password)


class BudgetService:
    _service = _BudgetService()

    @staticmethod
    def set_budget(user_id: int, category: str, limit: float, threshold: float = 0.8) -> Budget:
        return BudgetService._service.set_budget(user_id, category, limit, threshold)

    @staticmethod
    def check_alert(user_id: int, category: str, current_month_spend: float) -> Optional[str]:
        return BudgetService._service.check_alert(user_id, category, current_month_spend)


class TransactionService:
    _service = _TransactionService()

    @staticmethod
    def add_transaction(
        user_id: int,
        t_type: str,
        amount: float,
        date: str,
        category: str,
        description: str = "",
        currency: str = "USD",
        payment_method: str = "Cash",
        tags: str = "",
    ) -> Tuple[Transaction, Optional[str]]:
        return TransactionService._service.add_transaction(
            user_id=user_id,
            t_type=t_type,
            amount=amount,
            date=date,
            category=category,
            description=description,
            currency=currency,
            payment_method=payment_method,
            tags=tags,
        )

    @staticmethod
    def get_transactions(user_id: int) -> List[Transaction]:
        return TransactionService._service.get_transactions(user_id)

    @staticmethod
    def delete_transaction(user_id: int, transaction_id: int) -> bool:
        return TransactionService._service.delete_transaction(user_id, transaction_id)


class CSVService:
    _service = _CSVService()

    @staticmethod
    def export_transactions(user_id: int, filepath: str) -> int:
        return CSVService._service.export_transactions(user_id, filepath)

    @staticmethod
    def import_transactions(user_id: int, filepath: str) -> int:
        return CSVService._service.import_transactions(user_id, filepath)
