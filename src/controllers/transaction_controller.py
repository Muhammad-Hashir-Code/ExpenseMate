from typing import Optional, List, Dict, Tuple
from src.controllers.base_controller import BaseController
from src.core.result import Result
from src.models.entities import Transaction
from src.services.transaction_service import TransactionService
from src.services.csv_service import CSVService, ImportResult


class TransactionController(BaseController):
    """
    Controller handling transaction recording, querying, analytics, and CSV operations.
    Flow: Controller -> TransactionService / CSVService -> TransactionRepository -> Database.
    """

    def __init__(
        self,
        tx_service: Optional[TransactionService] = None,
        csv_service: Optional[CSVService] = None,
    ):
        self.tx_service = tx_service or TransactionService()
        self.csv_service = csv_service or CSVService()

    def create_transaction(
        self,
        user_id: int,
        t_type: str,
        amount_input: str,
        date_input: str,
        category: str,
        description: str = "",
        currency: str = "USD",
        payment_method: str = "Cash",
        tags: str = "",
    ) -> Result[Tuple[Transaction, Optional[str]]]:
        # Input Validation
        amount, err = self.parse_positive_float(amount_input, "Amount")
        if err:
            return self.failure(err)

        err = self.validate_presence(category, "Category")
        if err:
            return self.failure(err)

        err = self.validate_presence(date_input, "Date")
        if err:
            return self.failure(err)

        try:
            tx, alert = self.tx_service.add_transaction(
                user_id=user_id,
                t_type=t_type,
                amount=amount,
                date=date_input.strip(),
                category=category.strip(),
                description=description.strip() if description else "",
                currency=currency,
                payment_method=payment_method,
                tags=tags,
            )
            return self.success((tx, alert))
        except ValueError as e:
            return self.failure(str(e))
        except Exception as e:
            return self.failure(f"Failed to record transaction: {str(e)}")

    def get_transactions(self, user_id: int) -> Result[List[Transaction]]:
        try:
            transactions = self.tx_service.get_transactions(user_id)
            return self.success(transactions)
        except Exception as e:
            return self.failure(f"Failed to fetch transactions: {str(e)}")

    def delete_transaction(self, user_id: int, tx_id: int) -> Result[bool]:
        try:
            success = self.tx_service.delete_transaction(user_id, tx_id)
            if success:
                return self.success(True)
            return self.failure("Transaction not found or could not be deleted")
        except Exception as e:
            return self.failure(f"Failed to delete transaction: {str(e)}")

    def get_dashboard_summary(self, user_id: int) -> Result[Dict[str, float]]:
        try:
            summary = self.tx_service.get_dashboard_summary(user_id)
            return self.success(summary)
        except Exception as e:
            return self.failure(f"Failed to load dashboard summary: {str(e)}")

    def get_category_chart_data(self, user_id: int) -> Result[Dict[str, float]]:
        try:
            data = self.tx_service.get_category_breakdown(user_id)
            return self.success(data)
        except Exception as e:
            return self.failure(f"Failed to load category chart data: {str(e)}")

    def import_csv(self, user_id: int, filepath: str) -> Result[ImportResult]:
        err = self.validate_presence(filepath, "CSV File path")
        if err:
            return self.failure(err)

        try:
            result = self.csv_service.import_transactions_detailed(user_id, filepath)
            return self.success(result)
        except Exception as e:
            return self.failure(f"CSV Import failed: {str(e)}")

    def export_csv(self, user_id: int, filepath: str) -> Result[int]:
        err = self.validate_presence(filepath, "Export Destination path")
        if err:
            return self.failure(err)

        try:
            count = self.csv_service.export_transactions(user_id, filepath)
            return self.success(count)
        except Exception as e:
            return self.failure(f"CSV Export failed: {str(e)}")

