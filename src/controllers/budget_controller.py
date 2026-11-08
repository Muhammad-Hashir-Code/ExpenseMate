from typing import Optional, List, Dict
from src.controllers.base_controller import BaseController
from src.core.result import Result
from src.models.entities import Budget
from src.services.budget_service import BudgetService


class BudgetController(BaseController):
    """
    Controller handling category budget definitions, limit queries, and threshold alerts.
    Flow: Controller -> BudgetService -> BudgetRepository -> Database.
    """

    def __init__(self, budget_service: Optional[BudgetService] = None):
        self.budget_service = budget_service or BudgetService()

    def set_budget(
        self,
        user_id: int,
        category: str,
        limit_input: str,
        threshold_pct_input: str,
    ) -> Result[Budget]:
        # Input Validation
        err = self.validate_presence(category, "Category")
        if err:
            return self.failure(err)

        limit, err = self.parse_positive_float(limit_input, "Monthly Limit")
        if err:
            return self.failure(err)

        try:
            pct_val = float(threshold_pct_input)
            if pct_val <= 0 or pct_val > 100:
                return self.failure("Alert threshold must be between 1% and 100%")
            threshold = pct_val / 100.0
        except (ValueError, TypeError):
            return self.failure("Invalid numeric percentage for Alert Threshold")

        try:
            budget = self.budget_service.set_budget(
                user_id=user_id,
                category=category.strip(),
                limit=limit,
                threshold=threshold,
            )
            return self.success(budget)
        except ValueError as e:
            return self.failure(str(e))
        except Exception as e:
            return self.failure(f"Failed to save budget: {str(e)}")

    def get_budget_status(
        self, user_id: int, category: str, current_spend: float
    ) -> Result[Optional[Dict]]:
        try:
            status = self.budget_service.get_budget_status(
                user_id, category.strip(), current_spend
            )
            return self.success(status)
        except Exception as e:
            return self.failure(f"Failed to fetch budget status: {str(e)}")

    def get_all_budgets(self, user_id: int) -> Result[List[Budget]]:
        try:
            budgets = self.budget_service.get_all_budgets(user_id)
            return self.success(budgets)
        except Exception as e:
            return self.failure(f"Failed to fetch budgets: {str(e)}")

