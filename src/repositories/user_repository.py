import sqlite3
from typing import Optional
from src.models.entities import User
from src.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """Handles persistence and retrieval of User entities."""

    def create(self, user: User) -> User:
        conn = self.get_connection()
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
            raise ValueError(f"Username '{user.username}' already exists")
        finally:
            conn.close()

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                )
            return None
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                )
            return None
        finally:
            conn.close()

