import sqlite3
from src.core.config import Config


class BaseRepository:
    """Base repository providing database connections."""

    def __init__(self, db_path: str = None):
        self._db_path = db_path

    @property
    def db_path(self) -> str:
        if self._db_path:
            return self._db_path
        # Check database.DB_PATH dynamically for backward compatibility with test fixtures
        try:
            from src.data import database
            return getattr(database, "DB_PATH", Config.DB_PATH)
        except ImportError:
            return Config.DB_PATH

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
