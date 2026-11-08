# 🧪 Assignment 02 Deliverable: Test Package & Regression Report
**Project:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction & Development  
**Authors:** Muhammad Hashir (Member A), Muhammad Omer (Member B)  

---

## 1. Test Package Overview
The test package consists of 16 comprehensive automated test cases structured across 5 focused test suites in the `tests/` directory:

| Test Suite | File Path | Focus Area | Test Count |
|---|---|---|---|
| **Legacy Regression** | [`tests/test_services.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_services.py) | Verifies Assignment 01 baseline features remain operational. | 3 |
| **Migration & Schema** | [`tests/test_migration.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_migration.py) | Tests versioned migrations, schema integrity & legacy data preservation. | 2 |
| **Controller Validation** | [`tests/test_controllers.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_controllers.py) | Unit tests for Auth, Transaction, and Budget controllers and Result DTOs. | 3 |
| **Rewritten Classes** | [`tests/test_rewritten_classes.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_rewritten_classes.py) | In-depth tests for rewritten `TransactionService` and `CSVService`. | 3 |
| **Integration / System** | [`tests/test_integration.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py) | 5 end-to-end integration workflows through the 4-layer architecture. | 5 |
| **Total** | | | **16 Tests (100% Pass)** |

---

## 2. Five Mandatory Integration / System Workflows

### IT-01: User Registration & Authentication Lifecycle
* **Source:** [`test_it01_user_authentication_lifecycle`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L26-L53)
* **Layers Traced:** `AuthController` $\longrightarrow$ `AuthService` $\longrightarrow$ `UserRepository` $\longrightarrow$ SQLite DB.
* **Workflow:**
  1. Registers a new student account (`hashir_student`, `SecurePass2026!`).
  2. Asserts PBKDF2 salt and hash generation and database record assignment (`user.id is not None`).
  3. Attempts duplicate registration; asserts controller returns formatted error `"already exists"`.
  4. Tests valid login; verifies identity match.
  5. Tests invalid login attempt; asserts rejection.
* **Status:** ✅ **PASS**

### IT-02: Multi-Currency & Payment Method Transaction Ingestion
* **Source:** [`test_it02_multicurrency_transaction_ingestion`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L56-L113)
* **Layers Traced:** `TransactionController` $\longrightarrow$ `TransactionService` $\longrightarrow$ `TransactionRepository` $\longrightarrow$ SQLite DB.
* **Workflow:**
  1. Records multiple transactions spanning different currencies (`USD`, `EUR`, `PKR`) and payment methods (`Credit Card`, `Bank Transfer`, `Cash`).
  2. Queries transaction list through `TransactionController.get_transactions()`.
  3. Asserts correct data type conversions and persistence across all columns.
* **Status:** ✅ **PASS**

### IT-03: Budget Threshold Alert Lifecycle
* **Source:** [`test_it03_budget_threshold_alert_lifecycle`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L116-L167)
* **Layers Traced:** `BudgetController` $\longrightarrow$ `BudgetService` $\longrightarrow$ `BudgetRepository` and `TransactionController` $\longrightarrow$ `TransactionService` $\longrightarrow$ `TransactionRepository`.
* **Workflow:**
  1. Sets $500 monthly budget for "Travel" with 80% threshold ($400).
  2. Inserts $250 expense (50% utilization); verifies alert payload is `None`.
  3. Inserts $160 expense (Month-To-Date total = $410, 82% utilization); verifies alert payload triggers with exact message: `"ALERT: You have spent $410.00 (82.0%) in 'Travel'..."`.
  4. Queries `BudgetController.get_budget_status()` to verify `is_alert == True` and `remaining == 90.0`.
* **Status:** ✅ **PASS**

### IT-04: Robust CSV Processing with Fault Tolerance & Round-Trip Export
* **Source:** [`test_it04_csv_import_tolerance_and_export`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L170-L215)
* **Layers Traced:** `TransactionController` $\longrightarrow$ `CSVService` $\longrightarrow$ `TransactionRepository` $\longrightarrow$ File System / DB.
* **Workflow:**
  1. Prepares a 4-row CSV file containing 3 valid rows and 1 corrupt row (`CORRUPT_NUM`).
  2. Executes `TransactionController.import_csv()`; asserts non-atomic fault tolerance: 3 valid rows imported, corrupt row skipped with line number `3` logged.
  3. Exports records back to a new CSV file; verifies file contents match original records.
* **Status:** ✅ **PASS**

### IT-05: Database Schema Migration & System Data Regression
* **Source:** [`test_it05_database_schema_migration_regression`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L218-L277)
* **Layers Traced:** `MigrationManager` $\longrightarrow$ SQLite DB $\longrightarrow$ `TransactionController` $\longrightarrow$ `TransactionRepository`.
* **Workflow:**
  1. Provisions a legacy Assignment 01 database without `payment_method`, `tags`, or `schema_migrations`.
  2. Populates historical users and transactions.
  3. Executes `MigrationManager.run_migrations()`.
  4. Verifies historical records are preserved and assigned default values.
  5. Inserts new records through `TransactionController` utilizing new schema features seamlessly.
* **Status:** ✅ **PASS**

---

## 3. Regression Testing Evidence
All Assignment 01 test cases in [`tests/test_services.py`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_services.py) were executed to guarantee zero regressions:
1. `test_auth_service`: ✅ **PASS**
2. `test_budget_and_transaction_alerts`: ✅ **PASS**
3. `test_csv_import_export`: ✅ **PASS**

### Complete Test Execution Log
```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\92313\Downloads\ExpenseMate
configfile: pytest.ini
plugins: anyio-4.14.2, platformdirs-4.12.0
collected 16 items

tests/test_controllers.py::test_auth_controller_validation PASSED        [  6%]
tests/test_controllers.py::test_transaction_controller_validation PASSED [ 12%]
tests/test_controllers.py::test_budget_controller_validation PASSED      [ 18%]
tests/test_integration.py::test_it01_user_authentication_lifecycle PASSED [ 25%]
tests/test_integration.py::test_it02_multicurrency_transaction_ingestion PASSED [ 31%]
tests/test_integration.py::test_it03_budget_threshold_alert_lifecycle PASSED [ 37%]
tests/test_integration.py::test_it04_csv_import_tolerance_and_export PASSED [ 43%]
tests/test_integration.py::test_it05_database_schema_migration_regression PASSED [ 50%]
tests/test_migration.py::test_fresh_migration PASSED                     [ 56%]
tests/test_migration.py::test_legacy_database_migration_preserves_records PASSED [ 62%]
tests/test_rewritten_classes.py::test_rewritten_transaction_service_sql_aggregation PASSED [ 68%]
tests/test_rewritten_classes.py::test_rewritten_csv_service_header_validation PASSED [ 75%]
tests/test_rewritten_classes.py::test_rewritten_csv_service_malformed_rows_recovery PASSED [ 81%]
tests/test_services.py::test_auth_service PASSED                         [ 87%]
tests/test_services.py::test_budget_and_transaction_alerts PASSED        [ 93%]
tests/test_services.py::test_csv_import_export PASSED                    [100%]

============================= 16 passed in 6.68s ==============================
```

