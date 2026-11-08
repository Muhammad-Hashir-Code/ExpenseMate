from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Result(Generic[T]):
    """Standardized result wrapper for Controller and Service responses."""

    def __init__(self, is_success: bool, data: Optional[T] = None, error_message: Optional[str] = None):
        self.is_success = is_success
        self.data = data
        self.error_message = error_message

    @classmethod
    def success(cls, data: Optional[T] = None) -> "Result[T]":
        return cls(is_success=True, data=data)

    @classmethod
    def failure(cls, error_message: str) -> "Result[T]":
        return cls(is_success=False, error_message=error_message)

    def __bool__(self) -> bool:
        return self.is_success

    def __repr__(self) -> str:
        if self.is_success:
            return f"<Result: Success, data={self.data}>"
        return f"<Result: Failure, error='{self.error_message}'>"

