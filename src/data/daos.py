import sqlite3
from typing import List, Optional
from src.models.entities import User, Transaction, Budget
from src.data.database import get_connection


class UserDAO:
    @staticmethod
    def create(user: User) -> User:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (user.username, user.password_hash),
            )
            conn.commit()
            user.id = cursor.lastrowid
            return user
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError("Username already exists")
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
            )
        return None


class TransactionDAO:
    @staticmethod
    def create(transaction: Transaction) -> Transaction:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO transactions (user_id, type, amount, date, category, description, currency) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    transaction.user_id,
                    transaction.type,
                    transaction.amount,
                    transaction.date,
                    transaction.category,
                    transaction.description,
                    transaction.currency,
                ),
            )
            conn.commit()
            transaction.id = cursor.lastrowid
            return transaction
        finally:
            conn.close()

    @staticmethod
    def get_all_by_user(user_id: int) -> List[Transaction]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC",
                (user_id,),
            )
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row["id"],
                    user_id=row["user_id"],
                    type=row["type"],
                    amount=row["amount"],
                    date=row["date"],
                    category=row["category"],
                    description=row["description"],
                    currency=row["currency"] if "currency" in row.keys() and row["currency"] is not None else "USD",
                )
                for row in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def delete(transaction_id: int, user_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                (transaction_id, user_id),
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()


class BudgetDAO:
    @staticmethod
    def create_or_update(budget: Budget) -> Budget:
        conn = get_connection()
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

    @staticmethod
    def get_by_user_and_category(
        user_id: int, category: str
    ) -> Optional[Budget]:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM budgets WHERE user_id = ? AND category = ?",
                (user_id, category),
            )
            row = cursor.fetchone()
            if row:
                return Budget(
                    id=row["id"],
                    user_id=row["user_id"],
                    category=row["category"],
                    monthly_limit=row["monthly_limit"],
                    alert_threshold=row["alert_threshold"],
                )
            return None
        finally:
            conn.close()
