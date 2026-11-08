from typing import Optional, List, Dict
from src.core.config import Config
from src.models.entities import Budget
from src.repositories.budget_repository import BudgetRepository


class BudgetService:
    """Handles category budget definition, limit monitoring, and threshold alerting."""

    def __init__(self, budget_repo: Optional[BudgetRepository] = None):
        self.budget_repo = budget_repo or BudgetRepository()

    def set_budget(
        self, user_id: int, category: str, limit: float, threshold: float = None
    ) -> Budget:
        """Sets or updates a budget limit and alert threshold for a category."""
        category = category.strip()
        if not category:
            raise ValueError("Category cannot be empty")
        if limit <= 0:
            raise ValueError("Monthly budget limit must be greater than zero")

        if threshold is None:
            threshold = Config.DEFAULT_ALERT_THRESHOLD

        if threshold <= 0 or threshold > Config.MAX_ALERT_THRESHOLD:
            raise ValueError(
                f"Alert threshold must be between 0 and {Config.MAX_ALERT_THRESHOLD} (e.g. 0.8 for 80%)"
            )

        budget = Budget(
            user_id=user_id,
            category=category,
            monthly_limit=limit,
            alert_threshold=threshold,
        )
        return self.budget_repo.create_or_update(budget)

    def get_budget(self, user_id: int, category: str) -> Optional[Budget]:
        return self.budget_repo.get_by_user_and_category(user_id, category.strip())

    def get_all_budgets(self, user_id: int) -> List[Budget]:
        return self.budget_repo.get_all_by_user(user_id)

    def check_alert(
        self, user_id: int, category: str, current_month_spend: float
    ) -> Optional[str]:
        """Checks if current spending exceeds the category's alert threshold."""
        budget = self.budget_repo.get_by_user_and_category(user_id, category)
        if not budget:
            return None

        threshold_amount = budget.monthly_limit * budget.alert_threshold
        if current_month_spend >= threshold_amount:
            usage_pct = (current_month_spend / budget.monthly_limit) * 100
            return (
                f"ALERT: You have spent ${current_month_spend:.2f} ({usage_pct:.1f}%) in '{category}', "
                f"reaching/exceeding your threshold of ${threshold_amount:.2f} "
                f"(Monthly Limit: ${budget.monthly_limit:.2f})."
            )
        return None

    def get_budget_status(
        self, user_id: int, category: str, current_spend: float
    ) -> Optional[Dict]:
        """Returns structured budget progress statistics."""
        budget = self.budget_repo.get_by_user_and_category(user_id, category)
        if not budget:
            return None

        remaining = max(0.0, budget.monthly_limit - current_spend)
        percentage = (current_spend / budget.monthly_limit) * 100 if budget.monthly_limit > 0 else 0
        threshold_amt = budget.monthly_limit * budget.alert_threshold
        is_alert = current_spend >= threshold_amt

        return {
            "category": category,
            "monthly_limit": budget.monthly_limit,
            "alert_threshold": budget.alert_threshold,
            "threshold_amount": threshold_amt,
            "current_spend": current_spend,
            "remaining": remaining,
            "usage_percentage": percentage,
            "is_alert": is_alert,
        }

