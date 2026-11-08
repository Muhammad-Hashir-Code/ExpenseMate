# 📦 Assignment 02 Deliverable: Migration Report
**Project:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction & Development  
**Concept Demonstrated:** Part A — Migration (Move the System Forward)  
**Authors:** Muhammad Hashir (Member A), Muhammad Omer (Member B)  

---

## 1. Executive Summary & Migration Objective
In Assignment 01, ExpenseMate relied on ad-hoc schema patching using runtime `PRAGMA table_info` checks embedded inside `src/data/database.py`, unversioned helper scripts (`upgrade_db.py`), and hardcoded paths and configuration constants across various files. 

For Assignment 02, the team designed and executed a structured, production-grade **Database Schema Versioning & Configuration Externalization Migration**. This migration introduces:
1. A dedicated, repeatable `MigrationEngine` (`src/data/migrations/migration_manager.py`) tracking applied migrations via an internal `schema_migrations` audit table.
2. Formally versioned, incremental SQL migration files (`001_baseline_schema.sql`, `002_add_payment_methods_and_tags.sql`).
3. Externalized application configuration (`src/core/config.py`) decoupling database paths, PBKDF2 hashing parameters, supported currencies, and default payment methods from source code.
4. Schema evolution adding `payment_method` (`Cash`, `Credit Card`, `Debit Card`, `Bank Transfer`, `Other`) and `tags` columns to `transactions` with guaranteed zero data loss for existing records.

---

## 2. Before vs. Target State Comparison

| Aspect | Before State (Assignment 01) | Target State (Assignment 02 Migrated) |
|---|---|---|
| **Schema Tracking** | No version tracking table; ad-hoc runtime `PRAGMA table_info` queries inside `init_db()`. | Formal `schema_migrations` table recording `version`, `name`, and timestamp `applied_at`. |
| **Migration Execution** | Manual execution of loose scripts (`upgrade_db.py`) or ad-hoc table checks. | Automated, repeatable, idempotent migration manager (`python -m src.data.migrations.migration_manager`). |
| **Transaction Schema** | Columns: `id`, `user_id`, `type`, `amount`, `date`, `category`, `description`, `currency`. | Extended columns: adds `payment_method TEXT DEFAULT 'Cash'` and `tags TEXT DEFAULT ''`. |
| **Configuration** | Database paths (`expensemate.db`), PBKDF2 iterations (`100000`), and currency lists hardcoded across multiple files. | Centralized in `src/core/config.py` with environment variable override support (`EXPENSEMATE_DB_PATH`, `EXPENSEMATE_HASH_ITERATIONS`). |
| **Data Preservation** | Fragile alter queries risk table lock or duplicate column errors. | Non-destructive `ALTER TABLE` statements wrapped in transactions with graceful duplicate handling. |

---

## 3. Migration Procedure & Steps Performed

1. **Configuration Centralization:** Created [`src/core/config.py`](file:///C:/Users/92313/Downloads/ExpenseMate/src/core/config.py) establishing `Config.DB_PATH`, `Config.SUPPORTED_CURRENCIES`, `Config.SUPPORTED_PAYMENT_METHODS`, and security parameters.
2. **Migration Directory Structure:** Created `src/data/migrations/` containing:
   - `001_baseline_schema.sql`: Encapsulates initial tables (`schema_migrations`, `users`, `transactions`, `budgets`).
   - `002_add_payment_methods_and_tags.sql`: Adds `payment_method` and `tags` columns with non-null defaults.
3. **Migration Engine Construction:** Developed [`MigrationManager`](file:///C:/Users/92313/Downloads/ExpenseMate/src/data/migrations/migration_manager.py) to:
   - Identify unapplied migration files in sequential lexicographical order.
   - Detect pre-existing legacy databases and mark baseline migrations accordingly.
   - Execute migrations transactionally and log records to `schema_migrations`.
   - Provide `verify_migration_integrity()` for post-migration sanity checks.
4. **Domain Entity Alignment:** Updated [`Transaction`](file:///C:/Users/92313/Downloads/ExpenseMate/src/models/entities.py#L13-L24) dataclass with optional `payment_method: str = "Cash"` and `tags: str = ""` to preserve full backward compatibility.
5. **Database Initialization Hook:** Updated [`init_db()`](file:///C:/Users/92313/Downloads/ExpenseMate/src/data/database.py#L17-L21) in `database.py` to invoke `MigrationManager().run_migrations()` seamlessly upon app boot.

---

## 4. Risks & Compatibility Considerations

- **Risk 1: Duplicate Column Error on Existing Migrated Databases:**  
  *Mitigation:* `MigrationManager` captures `sqlite3.OperationalError` specifically checking for `"duplicate column name"` and skips safely, guaranteeing idempotency.
- **Risk 2: Breaking Existing Assignment 01 Test Fixtures:**  
  *Mitigation:* Repository connection providers dynamically check `database.DB_PATH` overrides so temporary test databases created by `pytest` fixtures receive clean schema migrations.
- **Risk 3: Corrupting Legacy Rows Without Payment Method:**  
  *Mitigation:* `ALTER TABLE transactions ADD COLUMN payment_method TEXT DEFAULT 'Cash'` ensures all historical records automatically receive a valid default value without `NULL` pointer errors.

---

## 5. Verification & Test Evidence

Migration functionality is continuously verified by automated test cases:
1. **Fresh Database Provisioning:** [`test_fresh_migration`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_migration.py#L7-L19) verifies all tables and columns are created on a blank database.
2. **Legacy Database Preservation:** [`test_legacy_database_migration_preserves_records`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_migration.py#L22-L78) provisions a mock Assignment 01 database with historical records, runs `MigrationManager`, and asserts:
   - All pre-existing users and transactions remain 100% intact.
   - New columns are added with correct defaults (`payment_method == 'Cash'`).
   - No data loss or schema corruption occurs.
3. **End-to-End System Regression:** [`test_it05_database_schema_migration_regression`](file:///C:/Users/92313/Downloads/ExpenseMate/tests/test_integration.py#L201-L260) confirms that the application controllers can immediately read legacy records and create new records with the extended schema.

```
tests/test_migration.py::test_fresh_migration PASSED
tests/test_migration.py::test_legacy_database_migration_preserves_records PASSED
tests/test_integration.py::test_it05_database_schema_migration_regression PASSED
```

