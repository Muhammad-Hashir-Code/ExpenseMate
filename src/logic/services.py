import hashlib
import os
import csv
from typing import List, Optional, Tuple
from datetime import datetime
from src.models.entities import User, Transaction, Budget
from src.data.daos import UserDAO, TransactionDAO, BudgetDAO


class AuthService:
    """Handles User Authentication and Registration."""

    @staticmethod
    def _hash_password(password: str, salt: bytes) -> str:
        """Helper to create a secure password hash using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100000
        ).hex()

    @staticmethod
    def register(username: str, password: str) -> User:
        """Registers a new user with a salted password hash (NFR-5)."""
        salt = os.urandom(16)
        hashed_pw = AuthService._hash_password(password, salt)
        stored_hash = f"{salt.hex()}:{hashed_pw}"

        user = User(username=username, password_hash=stored_hash)
        return UserDAO.create(user)

    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        """Validates credentials and returns the User if successful."""
        user = UserDAO.get_by_username(username)
        if not user:
            return None

        try:
            salt_hex, stored_hash = user.password_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            if AuthService._hash_password(password, salt) == stored_hash:
                return user
        except ValueError:
            pass
        return None


class BudgetService:
    """Handles setting budgets and evaluating alert thresholds."""

    @staticmethod
    def set_budget(
        user_id: int, category: str, limit: float, threshold: float
    ) -> Budget:
        """Sets or updates a budget limit and alert threshold for a category."""
        budget = Budget(
            user_id=user_id,
            category=category,
            monthly_limit=limit,
            alert_threshold=threshold,
        )
        return BudgetDAO.create_or_update(budget)

    @staticmethod
    def check_alert(
        user_id: int, category: str, current_month_spend: float
    ) -> Optional[str]:
        """Checks if current spending exceeds the category's budget threshold."""
        budget = BudgetDAO.get_by_user_and_category(user_id, category)
        if not budget:
            return None

        threshold_amount = budget.monthly_limit * budget.alert_threshold
        if current_month_spend >= threshold_amount:
            return (
                f"ALERT: You have spent ${current_month_spend:.2f} in '{category}', "
                f"reaching/exceeding your threshold of ${threshold_amount:.2f} "
                f"(Limit: ${budget.monthly_limit:.2f})."
            )
        return None


class TransactionService:
    """Handles managing income and expenses, and triggering budget checks."""

    @staticmethod
    def add_transaction(
        user_id: int,
        t_type: str,
        amount: float,
        date: str,
        category: str,
        description: str = "",
        currency: str = "USD",
    ) -> Tuple[Transaction, Optional[str]]:
        """
        Adds a transaction and automatically checks for budget alerts if it's an expense.
        Returns the transaction and an optional alert message.
        """
        t = Transaction(
            user_id=user_id,
            type=t_type,
            amount=amount,
            date=date,
            category=category,
            description=description,
            currency=currency,
        )
        t = TransactionDAO.create(t)

        alert_msg = None
        if t_type == "expense":
            # Calculate current month spend for this category to check against the budget
            transactions = TransactionDAO.get_all_by_user(user_id)
            t_date = datetime.strptime(date, "%Y-%m-%d")

            month_spend = sum(
                tx.amount
                for tx in transactions
                if tx.type == "expense"
                and tx.category == category
                and datetime.strptime(tx.date, "%Y-%m-%d").month
                == t_date.month
                and datetime.strptime(tx.date, "%Y-%m-%d").year == t_date.year
            )

            alert_msg = BudgetService.check_alert(
                user_id, category, month_spend
            )

        return t, alert_msg

    @staticmethod
    def get_transactions(user_id: int) -> List[Transaction]:
        """Retrieves all transactions for a user, sorted newest first."""
        return TransactionDAO.get_all_by_user(user_id)

    @staticmethod
    def delete_transaction(user_id: int, transaction_id: int) -> bool:
        """Deletes a specific transaction."""
        return TransactionDAO.delete(transaction_id, user_id)


class CSVService:
    """Handles CSV Import and Export operations."""

    @staticmethod
    def export_transactions(user_id: int, filepath: str):
        """Exports a user's transactions to a CSV file."""
        transactions = TransactionDAO.get_all_by_user(user_id)
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Type",
                    "Amount",
                    "Date",
                    "Category",
                    "Description",
                    "Currency",
                ]
            )
            for t in transactions:
                writer.writerow(
                    [
                        t.type,
                        t.amount,
                        t.date,
                        t.category,
                        t.description,
                        t.currency,
                    ]
                )

    @staticmethod
    def import_transactions(user_id: int, filepath: str) -> int:
        """Imports transactions from a CSV file. Expected headers: Type, Amount, Date, Category, Description."""
        imported_count = 0
        with open(filepath, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    TransactionService.add_transaction(
                        user_id=user_id,
                        t_type=row["Type"].lower(),
                        amount=float(row["Amount"]),
                        date=row["Date"],
                        category=row["Category"],
                        description=row.get("Description", ""),
                        currency=row.get("Currency", "USD"),
                    )
                    imported_count += 1
                except Exception as e:
                    # In a real app we might log this or collect errors
                    pass
        return imported_count
