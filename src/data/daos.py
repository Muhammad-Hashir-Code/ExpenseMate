"""
Data Access Layer facades providing backward-compatible DAO interface
backed by the new Repository layer.
"""
from typing import List, Optional
from src.models.entities import User, Transaction, Budget
from src.repositories.user_repository import UserRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.budget_repository import BudgetRepository


class UserDAO:
    _repo = UserRepository()

    @staticmethod
    def create(user: User) -> User:
        return UserDAO._repo.create(user)

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        return UserDAO._repo.get_by_username(username)


class TransactionDAO:
    _repo = TransactionRepository()

    @staticmethod
    def create(transaction: Transaction) -> Transaction:
        return TransactionDAO._repo.create(transaction)

    @staticmethod
    def get_all_by_user(user_id: int) -> List[Transaction]:
        return TransactionDAO._repo.get_all_by_user(user_id)

    @staticmethod
    def delete(transaction_id: int, user_id: int) -> bool:
        return TransactionDAO._repo.delete(transaction_id, user_id)


class BudgetDAO:
    _repo = BudgetRepository()

    @staticmethod
    def create_or_update(budget: Budget) -> Budget:
        return BudgetDAO._repo.create_or_update(budget)

    @staticmethod
    def get_by_user_and_category(user_id: int, category: str) -> Optional[Budget]:
        return BudgetDAO._repo.get_by_user_and_category(user_id, category)
