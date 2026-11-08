from typing import Optional
from src.controllers.base_controller import BaseController
from src.core.result import Result
from src.models.entities import User
from src.services.auth_service import AuthService


class AuthController(BaseController):
    """
    Controller handling user authentication workflows.
    Flow: Controller -> AuthService -> UserRepository -> Database.
    """

    def __init__(self, auth_service: Optional[AuthService] = None):
        self.auth_service = auth_service or AuthService()

    def register(self, username: str, password: str) -> Result[User]:
        # Basic input validation
        err = self.validate_presence(username, "Username")
        if err:
            return self.failure(err)
        err = self.validate_presence(password, "Password")
        if err:
            return self.failure(err)

        if len(password.strip()) < 4:
            return self.failure("Password must be at least 4 characters long")

        try:
            user = self.auth_service.register(username.strip(), password.strip())
            return self.success(user)
        except ValueError as e:
            return self.failure(str(e))
        except Exception as e:
            return self.failure(f"Registration failed: {str(e)}")

    def login(self, username: str, password: str) -> Result[User]:
        # Basic input validation
        err = self.validate_presence(username, "Username")
        if err:
            return self.failure(err)
        err = self.validate_presence(password, "Password")
        if err:
            return self.failure(err)

        try:
            user = self.auth_service.login(username.strip(), password.strip())
            if user:
                return self.success(user)
            return self.failure("Invalid username or password")
        except Exception as e:
            return self.failure(f"Login error: {str(e)}")

