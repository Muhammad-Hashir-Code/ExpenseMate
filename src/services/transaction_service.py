from datetime import datetime
from typing import List, Optional, Tuple, Dict
from src.core.config import Config
from src.models.entities import Transaction
from src.repositories.transaction_repository import TransactionRepository
from src.services.budget_service import BudgetService


class TransactionService:
    """
    Rewritten TransactionService.
    
    Major improvements over Assignment 01 baseline:
    1. Replaced O(N) application-level in-memory iterations and repetitive 
       `datetime.strptime` string parsing with direct SQL aggregation queries
       in `TransactionRepository.get_monthly_spending`.
    2. Input validation for types, ranges, date formats, currencies, and payment methods.
    3. Decoupled budget alert evaluation via dependency injection.
    4. Enhanced analytics methods (financial summary, category breakdown) leveraging SQL engine.
    """

    def __init__(
        self,
        tx_repo: Optional[TransactionRepository] = None,
        budget_service: Optional[BudgetService] = None,
    ):
        self.tx_repo = tx_repo or TransactionRepository()
        self.budget_service = budget_service or BudgetService()

    def _validate_transaction_inputs(
        self,
        t_type: str,
        amount: float,
        date_str: str,
        category: str,
        currency: str,
        payment_method: str,
    ):
        if t_type not in ("income", "expense"):
            raise ValueError("Transaction type must be 'income' or 'expense'")
        if amount <= 0:
            raise ValueError("Transaction amount must be greater than zero")
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
        
        # Validate date format (YYYY-MM-DD)
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD)")

        if currency not in Config.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency '{currency}'. Allowed: {', '.join(Config.SUPPORTED_CURRENCIES)}"
            )

        if payment_method not in Config.SUPPORTED_PAYMENT_METHODS:
            raise ValueError(
                f"Unsupported payment method '{payment_method}'. Allowed: {', '.join(Config.SUPPORTED_PAYMENT_METHODS)}"
            )

        return parsed_date

    def add_transaction(
        self,
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
        """
        Adds a transaction and evaluates budget alerts if the transaction is an expense.
        Uses optimized SQL aggregation instead of scanning all user records in Python.
        """
        t_type_clean = t_type.strip().lower()
        category_clean = category.strip()
        currency_clean = (currency or Config.DEFAULT_CURRENCY).strip().upper()
        payment_clean = (payment_method or Config.DEFAULT_PAYMENT_METHOD).strip()

        parsed_date = self._validate_transaction_inputs(
            t_type_clean, amount, date, category_clean, currency_clean, payment_clean
        )

        transaction = Transaction(
            user_id=user_id,
            type=t_type_clean,
            amount=amount,
            date=date,
            category=category_clean,
            description=description.strip() if description else "",
            currency=currency_clean,
            payment_method=payment_clean,
            tags=tags.strip() if tags else "",
        )
        saved_tx = self.tx_repo.create(transaction)

        alert_msg = None
        if t_type_clean == "expense":
            # Optimized SQL calculation for current month spend
            month_spend = self.tx_repo.get_monthly_spending(
                user_id=user_id,
                category=category_clean,
                year=parsed_date.year,
                month=parsed_date.month,
            )
            alert_msg = self.budget_service.check_alert(
                user_id=user_id,
                category=category_clean,
                current_month_spend=month_spend,
            )

        return saved_tx, alert_msg

    def get_transactions(self, user_id: int) -> List[Transaction]:
        """Retrieves all transactions for a user, sorted newest first."""
        return self.tx_repo.get_all_by_user(user_id)

    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        """Deletes a specific transaction."""
        return self.tx_repo.delete(transaction_id, user_id)

    def get_dashboard_summary(self, user_id: int) -> Dict[str, float]:
        """Retrieves aggregated balance, income, and expense directly from the database."""
        return self.tx_repo.get_financial_summary(user_id)

    def get_category_breakdown(self, user_id: int) -> Dict[str, float]:
        """Retrieves expense totals grouped by category directly via SQL."""
        return self.tx_repo.get_expenses_by_category(user_id)

