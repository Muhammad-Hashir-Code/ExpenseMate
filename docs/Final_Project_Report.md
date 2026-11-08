# 📘 Assignment 02: Final Project Report
**Project Title:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction & Development (CS-314)  
**Deliverable:** Assignment 02 Final Evolution Report  
**Team Members:** Muhammad Hashir (Member A), Muhammad Omer (Member B)  
**Submission Date:** November 2026  

---

## 1. Executive Summary
ExpenseMate is a desktop personal finance manager built in Python with SQLite and CustomTkinter. In Assignment 01, the system achieved core functionality for recording transactions, calculating budgets, and rendering visual spending charts. Assignment 02 evolved this codebase through three mandatory software construction concepts:
1. **Migration (Part A):** Transitioned from ad-hoc schema patching to an automated, versioned database migration engine (`MigrationManager`) and externalized configuration management (`src/core/config.py`). Extended the schema with `payment_method` and `tags` columns while preserving existing data.
2. **Layered Refactoring (Part B):** Restructured the application to follow a strict 4-layer dependency model:  
   $$\text{Controller} \longrightarrow \text{Services} \longrightarrow \text{Repository} \longrightarrow \text{Database}$$
   Eliminated direct database access from controllers and UI views, moved business calculations out of repositories, and standardized communications using the `Result[T]` pattern.
3. **Class Rewriting (Part C):** Replaced two problematic modules (`TransactionService` and `CSVService`) with modernized, highly efficient, and fault-tolerant implementations, eliminating $O(N)$ in-memory loops and silent exception swallowing.
4. **Quality & Maintainability Assurance:** Expanded test coverage across 16 automated tests (including 5 integration workflows), achieving **86% test coverage** and maintaining an overall **Grade A** in Cyclomatic Complexity (2.55 average) and Maintainability Index across all modules.

---

## 2. Concept 1: Migration (Part A)

### 2.1 Problem & Motivation
In Assignment 01, database evolution relied on ad-hoc runtime `PRAGMA table_info` checks embedded directly in `database.py` and loose standalone scripts (`upgrade_db.py`). Furthermore, database file paths, cryptographic parameters, and currency definitions were hardcoded across multiple files, creating high maintenance friction.

### 2.2 Implemented Solution
- **Externalized Configuration:** Created [`src/core/config.py`](file:///C:/Users/92313/Downloads/ExpenseMate/src/core/config.py) declaring centralized properties:
  - `DB_PATH`, `MIGRATIONS_DIR` (overridable via environment variables).
  - `SUPPORTED_CURRENCIES` (`USD`, `EUR`, `GBP`, `PKR`, `INR`).
  - `SUPPORTED_PAYMENT_METHODS` (`Cash`, `Credit Card`, `Debit Card`, `Bank Transfer`, `Other`).
  - `PBKDF2_ITERATIONS` ($100,000$) and salt byte length ($16$).
- **Versioned Migration Framework:** Implemented [`MigrationManager`](file:///C:/Users/92313/Downloads/ExpenseMate/src/data/migrations/migration_manager.py) and migrations in `src/data/migrations/`:
  - `001_baseline_schema.sql`: Core tables and audit log `schema_migrations`.
  - `002_add_payment_methods_and_tags.sql`: Extends `transactions` table with `payment_method TEXT DEFAULT 'Cash'` and `tags TEXT DEFAULT ''`.
- **Integrity & Backward Compatibility:** Provided automatic detection of pre-existing Assignment 01 databases. Existing records are preserved with default values and zero data loss.

---

## 3. Concept 2: Layered Refactoring (Part B)

### 3.1 Architectural Transformation
Assignment 02 strictly complies with the required 4-layer dependency hierarchy:

```
Controller Layer (src/controllers/)
       │  (Input validation, Result[T] packaging)
       ▼
Services Layer (src/services/)
       │  (Business rules, threshold evaluations, workflows)
       ▼
Repository Layer (src/repositories/)
       │  (Parameterized SQL, DB aggregations, Entity mapping)
       ▼
Database Layer (SQLite)
```

### 3.2 Refactored Features
1. **Transaction Management:**  
   `TransactionView` $\longrightarrow$ `TransactionController.create_transaction()` $\longrightarrow$ `TransactionService.add_transaction()` $\longrightarrow$ `TransactionRepository.create()` $\longrightarrow$ SQLite DB.
2. **Budgeting & Alert Monitoring:**  
   `BudgetView` $\longrightarrow$ `BudgetController.set_budget()` $\longrightarrow$ `BudgetService.set_budget()` $\longrightarrow$ `BudgetRepository.create_or_update()` $\longrightarrow$ SQLite DB.
3. **Financial Overview Analytics:**  
   `DashboardView` $\longrightarrow$ `TransactionController.get_dashboard_summary()` $\longrightarrow$ `TransactionRepository.get_financial_summary()` (runs SQL `SUM(CASE WHEN ...)`).

### 3.3 Key Architectural Benefits
- **Zero SQL in UI or Controllers:** SQL queries are strictly confined to repositories.
- **Zero UI in Business Logic:** Services accept pure data types and domain entities.
- **Decoupled Error Handling:** Standardized `Result[T]` pattern eliminates messy exception handlers in UI frames.

---

## 4. Concept 3: Rewriting Selected Classes (Part C)

### 4.1 Class 1 Rewrite: `TransactionService`
- **Original Defects:** On every transaction addition, loaded all user transactions from disk and iterated in Python with `datetime.strptime()` inside a list comprehension to compute current month expenses.
- **Rewritten Design:** Delegated monthly spend calculation to `TransactionRepository.get_monthly_spending()`, which executes an indexed SQL aggregation:
  ```sql
  SELECT COALESCE(SUM(amount), 0.0) FROM transactions 
  WHERE user_id = ? AND type = 'expense' AND category = ? 
    AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
  ```
- **Result:** $O(N)$ memory and CPU overhead replaced with an $O(1)$ database aggregation. Maintainability Index improved from **49.24** to **65.94**.

### 4.2 Class 2 Rewrite: `CSVService`
- **Original Defects:** Bare `except Exception: pass` silently swallowed all corrupted rows and errors. Lacked header validation, fired redundant budget alerts for every row, and had no transaction rollback.
- **Rewritten Design:** Implemented strict schema verification (`REQUIRED_HEADERS`), line-by-line validation logging exact row numbers and failure reasons, structured `ImportResult` summary, and atomic batch ingestion via `TransactionRepository.create_batch()`.
- **Result:** Robust error diagnostics, prevention of dirty imports, and high ingestion throughput.

---

## 5. Verification, Testing & Maintainability

### 5.1 Test Suite Breakdown
16 automated tests were executed via pytest:
- `test_services.py` (3 tests): Regression testing for Assignment 01 baseline.
- `test_migration.py` (2 tests): Migration engine and legacy database preservation.
- `test_controllers.py` (3 tests): Controller input validation and result wrappers.
- `test_rewritten_classes.py` (3 tests): SQL aggregation accuracy and CSV fault tolerance.
- `test_integration.py` (5 tests): Full workflows (IT-01 through IT-05).

**Execution Result:** 16 passed in 6.68 seconds, with **86% statement coverage** across 1,166 statements.

### 5.2 Maintainability Metrics Summary
- **Cyclomatic Complexity (Radon CC):** 150 blocks analyzed across the codebase, achieving an average score of **2.55 (Grade A)**.
- **Maintainability Index (Radon MI):** Every single module scored **Grade A** ($>65$), with repositories scoring up to **100.00**.

---

## 6. Demonstration Checklist & Q&A Defense

| Demonstration Item | Live Step to Perform | Expected Verification Output |
|---|---|---|
| **1. Migration Demo** | Run `python -m src.data.migrations.migration_manager` | Shows applied migrations, created `schema_migrations`, and verified `payment_method` column. |
| **2. Layer Trace Demo** | Add transaction in UI or run `test_it02` | Traces flow: `TransactionView` $\rightarrow$ `TransactionController` $\rightarrow$ `TransactionService` $\rightarrow$ `TransactionRepository` $\rightarrow$ DB. |
| **3. Rewritten Classes Demo** | Run `test_rewritten_classes.py` | Shows SQL-based monthly spending query and CSV import skipping malformed rows with line numbers. |
| **4. Test & Regression Demo**| Run `pytest -v` | Confirms all 16 unit and integration test cases pass (100% success). |

### Defense Questions: Challenges, Trade-offs & Lessons Learned

#### Concept 1: Migration
- **Challenge:** Preserving backward compatibility with databases created in Assignment 01 that lacked the `schema_migrations` table.
- **Trade-off:** Chose SQLite `ALTER TABLE` over table recreation. While SQLite alter table is limited, adding nullable/default columns is fast, non-destructive, and eliminates data copying risks.
- **Lesson Learned:** Always make migration scripts idempotent and maintain a formal version audit log from day one.

#### Concept 2: Layered Refactoring
- **Challenge:** Decoupling UI event handlers from service business logic without duplicating code.
- **Trade-off:** Introducing a dedicated Controller layer added slightly more boilerplate files, but completely decoupled UI widgets from data processing and simplified automated testing.
- **Lesson Learned:** Clear layer boundaries with explicit dependency directions prevent spaghetti code and make testing individual layers trivial.

#### Concept 3: Rewriting Classes
- **Challenge:** Completely replacing `TransactionService` and `CSVService` without breaking the public interface expected by legacy callers.
- **Trade-off:** In `CSVService`, offered both a rich detailed method (`import_transactions_detailed`) and a backward-compatible wrapper (`import_transactions`).
- **Lesson Learned:** When a class exhibits multiple architectural code smells, a clean rewrite with strict contracts is faster, safer, and cleaner than incremental refactoring.

---

## 7. Team Contributions

| Team Member | Primary Assigned Responsibilities |
|---|---|
| **Muhammad Hashir (Member A)** | Baseline Tagging, Configuration Management (`config.py`), Migration Engine (`migration_manager.py`), Controller Layer (`AuthController`, `TransactionController`), Rewriting `CSVService`, Migration Report, Refactoring Report. |
| **Muhammad Omer (Member B)** | Repository Layer (`UserRepository`, `TransactionRepository`, `BudgetRepository`), `BudgetController`, Rewriting `TransactionService` (SQL aggregation), Integration & System Tests (IT-01 to IT-05), Rewriting Report, Maintainability Analysis. |

Both team members contributed jointly to the final project report, code reviews, and demonstration preparation.

