import csv
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.core.config import Config
from src.models.entities import Transaction
from src.repositories.transaction_repository import TransactionRepository


@dataclass
class ImportResult:
    """Detailed summary of a CSV import operation."""
    total_rows: int = 0
    imported_count: int = 0
    skipped_count: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.imported_count > 0 and len(self.errors) == 0


class CSVService:
    """
    Rewritten CSVService.
    
    Major improvements over Assignment 01 baseline:
    1. Replaced silent exception swallowing (`except Exception: pass`) with strict row-level
       validation, logging error messages, and line number reporting.
    2. Strict header verification against required schema.
    3. Bulk transaction insertion avoiding N+1 repetitive budget alert evaluations.
    4. Provides structured `ImportResult` detailing succeeded vs failed rows.
    5. Clean dialect handling and backward-compatible helper methods.
    """

    REQUIRED_HEADERS = {"Type", "Amount", "Date", "Category"}

    def __init__(self, tx_repo: Optional[TransactionRepository] = None):
        self.tx_repo = tx_repo or TransactionRepository()

    def export_transactions(self, user_id: int, filepath: str) -> int:
        """Exports all transactions for a user to a CSV file."""
        transactions = self.tx_repo.get_all_by_user(user_id)
        # Ensure parent directory exists
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [
                    "Type",
                    "Amount",
                    "Date",
                    "Category",
                    "Description",
                    "Currency",
                    "PaymentMethod",
                    "Tags",
                ]
            )
            for t in transactions:
                writer.writerow(
                    [
                        t.type,
                        f"{t.amount:.2f}",
                        t.date,
                        t.category,
                        t.description or "",
                        t.currency or Config.DEFAULT_CURRENCY,
                        getattr(t, "payment_method", Config.DEFAULT_PAYMENT_METHOD),
                        getattr(t, "tags", ""),
                    ]
                )
        return len(transactions)

    def import_transactions_detailed(
        self, user_id: int, filepath: str, atomic: bool = False
    ) -> ImportResult:
        """
        Parses and validates CSV transactions, recording detailed error diagnostics.
        If atomic=True, rolls back the entire batch if any row fails validation.
        """
        result = ImportResult()
        if not os.path.exists(filepath):
            result.errors.append({"line": 0, "error": f"File '{filepath}' not found"})
            return result

        valid_transactions: List[Transaction] = []

        with open(filepath, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            
            # 1. Validate headers
            if not reader.fieldnames:
                result.errors.append({"line": 1, "error": "CSV file is empty or missing header row"})
                return result

            # Normalize header names (strip whitespace)
            clean_headers = {h.strip() for h in reader.fieldnames if h}
            missing = self.REQUIRED_HEADERS - clean_headers
            if missing:
                result.errors.append({
                    "line": 1,
                    "error": f"Missing required headers: {', '.join(sorted(missing))}"
                })
                return result

            # 2. Validate rows line-by-line
            for line_no, row in enumerate(reader, start=2):
                result.total_rows += 1
                try:
                    # Clean dictionary keys
                    clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}

                    # Type validation
                    raw_type = clean_row.get("Type", "").lower()
                    if raw_type not in ("income", "expense"):
                        raise ValueError(f"Invalid type '{raw_type}'. Expected 'income' or 'expense'")

                    # Amount validation
                    raw_amount = clean_row.get("Amount", "")
                    try:
                        amount = float(raw_amount)
                        if amount <= 0:
                            raise ValueError("Amount must be greater than zero")
                    except ValueError:
                        raise ValueError(f"Invalid numeric amount '{raw_amount}'")

                    # Date validation
                    raw_date = clean_row.get("Date", "")
                    try:
                        datetime.strptime(raw_date, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Invalid date '{raw_date}'. Expected format YYYY-MM-DD")

                    # Category validation
                    category = clean_row.get("Category", "")
                    if not category:
                        raise ValueError("Category cannot be empty")

                    # Optional fields
                    description = clean_row.get("Description", "")
                    currency = clean_row.get("Currency", Config.DEFAULT_CURRENCY).upper()
                    if currency not in Config.SUPPORTED_CURRENCIES:
                        currency = Config.DEFAULT_CURRENCY
                    
                    payment_method = clean_row.get("PaymentMethod", Config.DEFAULT_PAYMENT_METHOD)
                    tags = clean_row.get("Tags", "")

                    tx = Transaction(
                        user_id=user_id,
                        type=raw_type,
                        amount=amount,
                        date=raw_date,
                        category=category,
                        description=description,
                        currency=currency,
                        payment_method=payment_method,
                        tags=tags,
                    )
                    valid_transactions.append(tx)

                except Exception as err:
                    result.skipped_count += 1
                    result.errors.append({
                        "line": line_no,
                        "raw_data": row,
                        "error": str(err)
                    })

        # 3. Handle batch insertion
        if atomic and result.skipped_count > 0:
            # Atomic mode aborted due to validation errors
            result.imported_count = 0
            return result

        if valid_transactions:
            self.tx_repo.create_batch(valid_transactions)
            result.imported_count = len(valid_transactions)

        return result

    def import_transactions(self, user_id: int, filepath: str) -> int:
        """Backward-compatible import helper returning the number of imported records."""
        result = self.import_transactions_detailed(user_id, filepath, atomic=False)
        return result.imported_count

