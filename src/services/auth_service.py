import hashlib
import os
from typing import Optional
from src.core.config import Config
from src.models.entities import User
from src.repositories.user_repository import UserRepository


class AuthService:
    """Handles User Authentication and Registration with PBKDF2 hashing."""

    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def _hash_password(self, password: str, salt: bytes) -> str:
        """Helper to create a secure password hash using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            Config.PBKDF2_ITERATIONS,
        ).hex()

    def register(self, username: str, password: str) -> User:
        """Registers a new user with a salted password hash."""
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be empty")
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters long")

        salt = os.urandom(Config.SALT_BYTE_LENGTH)
        hashed_pw = self._hash_password(password, salt)
        stored_hash = f"{salt.hex()}:{hashed_pw}"

        user = User(username=username, password_hash=stored_hash)
        return self.user_repo.create(user)

    def login(self, username: str, password: str) -> Optional[User]:
        """Validates credentials and returns the User if authentication succeeds."""
        username = username.strip()
        if not username or not password:
            return None

        user = self.user_repo.get_by_username(username)
        if not user:
            return None

        try:
            salt_hex, stored_hash = user.password_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            if self._hash_password(password, salt) == stored_hash:
                return user
        except ValueError:
            pass
        return None

