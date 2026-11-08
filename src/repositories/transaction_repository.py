import sqlite3
from typing import List, Optional, Dict
from src.models.entities import Transaction
from src.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository):
    """Handles persistence, retrieval, and SQL aggregations for Transaction entities."""

    def _row_to_entity(self, row: sqlite3.Row) -> Transaction:
        row_keys = row.keys()
        return Transaction(
            id=row["id"],
            user_id=row["user_id"],
            type=row["type"],
            amount=row["amount"],
            date=row["date"],
            category=row["category"],
            description=row["description"] if "description" in row_keys and row["description"] is not None else "",
            currency=row["currency"] if "currency" in row_keys and row["currency"] is not None else "USD",
            payment_method=row["payment_method"] if "payment_method" in row_keys and row["payment_method"] is not None else "Cash",
            tags=row["tags"] if "tags" in row_keys and row["tags"] is not None else "",
        )

    def create(self, transaction: Transaction) -> Transaction:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO transactions 
                   (user_id, type, amount, date, category, description, currency, payment_method, tags) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    transaction.user_id,
                    transaction.type,
                    transaction.amount,
                    transaction.date,
                    transaction.category,
                    transaction.description,
                    transaction.currency,
                    transaction.payment_method,
                    transaction.tags,
                ),
            )
            conn.commit()
            transaction.id = cursor.lastrowid
            return transaction
        finally:
            conn.close()

    def create_batch(self, transactions: List[Transaction]) -> int:
        """Atomically inserts a batch of transactions in a single transaction block."""
        if not transactions:
            return 0
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            for t in transactions:
                cursor.execute(
                    """INSERT INTO transactions 
                       (user_id, type, amount, date, category, description, currency, payment_method, tags) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        t.user_id,
                        t.type,
                        t.amount,
                        t.date,
                        t.category,
                        t.description,
                        t.currency,
                        t.payment_method,
                        t.tags,
                    ),
                )
            conn.commit()
            return len(transactions)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_all_by_user(self, user_id: int) -> List[Transaction]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC",
                (user_id,),
            )
            return [self._row_to_entity(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, tx_id: int, user_id: int) -> Optional[Transaction]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
                (tx_id, user_id),
            )
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None
        finally:
            conn.close()

    def delete(self, tx_id: int, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                (tx_id, user_id),
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    def get_monthly_spending(self, user_id: int, category: str, year: int, month: int) -> float:
        """
        Calculates total spending for a specific user, category, month, and year
        directly in the database using SQL aggregation. Eliminates O(N) application loops.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # month formatted with 2 digits
            month_str = f"{month:02d}"
            year_str = str(year)
            cursor.execute(
                """SELECT COALESCE(SUM(amount), 0.0) as total 
                   FROM transactions 
                   WHERE user_id = ? 
                     AND type = 'expense' 
                     AND category = ? 
                     AND strftime('%Y', date) = ? 
                     AND strftime('%m', date) = ?""",
                (user_id, category, year_str, month_str),
            )
            row = cursor.fetchone()
            return float(row["total"]) if row else 0.0
        finally:
            conn.close()

    def get_financial_summary(self, user_id: int) -> Dict[str, float]:
        """Calculates total income, total expense, and net balance via SQL aggregation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """SELECT 
                     COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0.0) as income,
                     COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0.0) as expense
                   FROM transactions 
                   WHERE user_id = ?""",
                (user_id,),
            )
            row = cursor.fetchone()
            income = float(row["income"]) if row else 0.0
            expense = float(row["expense"]) if row else 0.0
            return {
                "income": income,
                "expense": expense,
                "balance": income - expense,
            }
        finally:
            conn.close()

    def get_expenses_by_category(self, user_id: int) -> Dict[str, float]:
        """Returns dictionary of category -> total spending via SQL GROUP BY."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """SELECT category, COALESCE(SUM(amount), 0.0) as total 
                   FROM transactions 
                   WHERE user_id = ? AND type = 'expense' 
                   GROUP BY category 
                   ORDER BY total DESC""",
                (user_id,),
            )
            return {row["category"]: float(row["total"]) for row in cursor.fetchall()}
        finally:
            conn.close()

