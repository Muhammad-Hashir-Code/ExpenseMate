import sqlite3
from typing import List, Optional
from src.models.entities import Budget
from src.repositories.base_repository import BaseRepository


class BudgetRepository(BaseRepository):
    """Handles persistence and retrieval of Budget entities."""

    def _row_to_entity(self, row: sqlite3.Row) -> Budget:
        return Budget(
            id=row["id"],
            user_id=row["user_id"],
            category=row["category"],
            monthly_limit=row["monthly_limit"],
            alert_threshold=row["alert_threshold"],
        )

    def create_or_update(self, budget: Budget) -> Budget:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO budgets (user_id, category, monthly_limit, alert_threshold) 
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(user_id, category) DO UPDATE SET 
                   monthly_limit = excluded.monthly_limit,
                   alert_threshold = excluded.alert_threshold""",
                (
                    budget.user_id,
                    budget.category,
                    budget.monthly_limit,
                    budget.alert_threshold,
                ),
            )
            conn.commit()
            if cursor.lastrowid:
                budget.id = cursor.lastrowid
            return budget
        finally:
            conn.close()

    def get_by_user_and_category(self, user_id: int, category: str) -> Optional[Budget]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM budgets WHERE user_id = ? AND category = ?",
                (user_id, category),
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
        finally:
            conn.close()

    def get_all_by_user(self, user_id: int) -> List[Budget]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM budgets WHERE user_id = ? ORDER BY category ASC",
                (user_id,),
            )
            return [self._row_to_entity(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def delete(self, budget_id: int, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM budgets WHERE id = ? AND user_id = ?",
                (budget_id, user_id),
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

