from typing import Optional
from src.core.result import Result


class BaseController:
    """Base controller with shared response and validation utilities."""

    @staticmethod
    def success(data=None) -> Result:
        return Result.success(data)

    @staticmethod
    def failure(error_message: str) -> Result:
        return Result.failure(error_message)

    @staticmethod
    def validate_presence(value: Optional[str], field_name: str) -> Optional[str]:
        if value is None or not str(value).strip():
            return f"{field_name} is required"
        return None

    @staticmethod
    def parse_positive_float(value_str: str, field_name: str) -> tuple[Optional[float], Optional[str]]:
        try:
            val = float(value_str)
            if val <= 0:
                return None, f"{field_name} must be greater than zero"
            return val, None
        except (ValueError, TypeError):
            return None, f"Invalid numeric format for {field_name}"

