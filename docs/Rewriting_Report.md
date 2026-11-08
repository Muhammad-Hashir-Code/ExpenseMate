# ✏️ Assignment 02 Deliverable: Rewriting Report
**Project:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction & Development  
**Concept Demonstrated:** Part C — Rewriting Selected Classes  
**Authors:** Muhammad Hashir (Member A), Muhammad Omer (Member B)  

---

## 1. Selection & Justification for Rewriting

Rather than applying cosmetic refactorings or reformatting code, two classes with deep architectural flaws, performance bottlenecks, and design anti-patterns were selected for complete ground-up rewrites:
1. **`TransactionService`** (formerly in `src/logic/services.py`)
2. **`CSVService`** (formerly in `src/logic/services.py`)

---

## 2. Class 1: `TransactionService`

### Original Responsibility & Severe Flaws
In Assignment 01, `TransactionService.add_transaction()` was responsible for creating transactions and evaluating budget thresholds. However, its implementation suffered from critical anti-patterns:
- **$O(N)$ In-Memory Linear Scan:** On *every single expense insertion*, `TransactionDAO.get_all_by_user(user_id)` was called, loading the user's entire lifetime transaction history into application memory.
- **Repeated String-to-Date Parsing:** Inside a Python list comprehension, it executed `datetime.strptime(tx.date, "%Y-%m-%d")` repeatedly on every historical record to extract the month and year.
- **Tight Coupling:** Statically coupled to `BudgetService.check_alert()`, making isolated unit testing impossible without setting up global state.
- **Missing Domain Validation:** Did not validate date formats, zero/negative amounts, or supported currencies.

### Rewritten Design & Architecture
The rewritten [`TransactionService`](file:///C:/Users/92313/Downloads/ExpenseMate/src/services/transaction_service.py) in `src/services/transaction_service.py` completely eliminates application-level scanning:
1. **SQL-Level Aggregation:** Month-to-date spending is calculated directly by the database engine via [`TransactionRepository.get_monthly_spending()`](file:///C:/Users/92313/Downloads/ExpenseMate/src/repositories/transaction_repository.py#L123-L147):
   ```sql
   SELECT COALESCE(SUM(amount), 0.0) as total 
   FROM transactions 
   WHERE user_id = ? 
     AND type = 'expense' 
     AND category = ? 
     AND strftime('%Y', date) = ? 
     AND strftime('%m', date) = ?
   ```
   Query execution time remains $O(1)$ relative to total transactions when indexed.
2. **Strict Pre-Condition Validation:** Added `_validate_transaction_inputs()` checking transaction types (`income`/`expense`), positive amounts, ISO date format compliance, and whitelisted currencies (`Config.SUPPORTED_CURRENCIES`).
3. **Decoupled Architecture:** `BudgetService` and `TransactionRepository` are injected via constructor, supporting mock-based testing.
4. **Behavior Preserved:** Public method signature `add_transaction(user_id, t_type, amount, date, category, ...)` continues to return `(transaction, alert_msg)` for backward compatibility.

---

## 3. Class 2: `CSVService`

### Original Responsibility & Severe Flaws
In Assignment 01, `CSVService` handled importing and exporting transactions. It had the following major design and reliability flaws:
- **Silent Exception Swallowing:** Contained a bare `except Exception: pass` block in `import_transactions()`. If a row had a corrupted amount, bad date, or missing category, the error was silently discarded with zero feedback to the user or system log.
- **$N+1$ Repetitive Alert Invocations:** Imported rows by invoking `TransactionService.add_transaction()` in a loop, triggering repetitive budget recalculations and alert evaluations for every line in a 1,000-row file.
- **Zero Header/Schema Validation:** Did not check if required headers (`Type`, `Amount`, `Date`, `Category`) were present, causing misaligned column inserts or crashes on unexpected CSV structures.
- **No Transaction Atomicity:** A partially corrupted CSV would leave half-imported dirty data in the database with no rollback option.

### Rewritten Design & Architecture
The rewritten [`CSVService`](file:///C:/Users/92313/Downloads/ExpenseMate/src/services/csv_service.py) in `src/services/csv_service.py` provides an enterprise-grade ingestion and export engine:
1. **Schema & Header Verification:** Validates that all required headers (`REQUIRED_HEADERS = {"Type", "Amount", "Date", "Category"}`) exist before attempting to parse any rows.
2. **Line-by-Line Diagnostics:** Captures exact line numbers, raw row values, and specific error reasons (e.g., `"Invalid numeric amount 'abc'"`, `"Invalid date '2026-15-99'"`).
3. **Structured `ImportResult` DTO:** Returns a detailed summary dataclass:
   ```python
   @dataclass
   class ImportResult:
       total_rows: int
       imported_count: int
       skipped_count: int
       errors: List[Dict[str, Any]]
   ```
4. **Atomic Batch Ingestion:** Validates all records first, then bulk-inserts them via [`TransactionRepository.create_batch()`](file:///C:/Users/92313/Downloads/ExpenseMate/src/repositories/transaction_repository.py#L51-L82) wrapped inside `BEGIN TRANSACTION ... COMMIT / ROLLBACK`.
5. **No Alert Storms:** Batch inserts bypass redundant budget alert evaluations during large bulk imports.
6. **Behavior Preserved:** Provides both `import_transactions_detailed()` for rich UI diagnostics and `import_transactions()` returning `int` for backward compatibility.

---

## 4. Test Verification for Rewritten Classes

Dedicated unit tests in [`tests/test_rewritten_classes.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_rewritten_classes.py) prove that the rewritten classes function correctly:
- [`test_rewritten_transaction_service_sql_aggregation`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_rewritten_classes.py#L25-L73): Verifies that SQL aggregation correctly isolates spending to the exact category, month, and year, without cross-month or cross-category alert bleeding.
- [`test_rewritten_csv_service_header_validation`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_rewritten_classes.py#L76-L88): Confirms that CSV files with missing headers are immediately rejected with descriptive error messages.
- [`test_rewritten_csv_service_malformed_rows_recovery`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_rewritten_classes.py#L91-L121): Verifies that non-atomic import successfully ingests valid rows while logging line numbers and reasons for skipped rows, and that atomic import safely rolls back.

```
tests/test_rewritten_classes.py::test_rewritten_transaction_service_sql_aggregation PASSED
tests/test_rewritten_classes.py::test_rewritten_csv_service_header_validation PASSED
tests/test_rewritten_classes.py::test_rewritten_csv_service_malformed_rows_recovery PASSED
```

