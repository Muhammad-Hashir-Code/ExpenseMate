# 📊 Assignment 02 Deliverable: Change Log & Maintainability Comparison
**Project:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction & Development  
**Authors:** Muhammad Hashir (Member A), Muhammad Omer (Member B)  

---

## 1. Before vs. After Maintainability Comparison

Measurements were gathered using:
1. **Radon Cyclomatic Complexity (`radon cc src/ -s -a`)**: Analyzes control-flow graphs and branch decisions.
2. **Radon Maintainability Index (`radon mi src/ -s`)**: Halstead volume, cyclomatic complexity, and lines of code combined into a 0–100 scale ($>65 = \text{Grade A}$).
3. **Coverage.py (`coverage run -m pytest tests/ ; coverage report`)**: Statement and branch execution verification.

### Metric 1: Cyclomatic Complexity (CC)
| Component | Assignment 01 (Baseline) | Assignment 02 (Evolved) | Improvement & Analysis |
|---|---|---|---|
| `DashboardView.refresh_data` | **5** (Grade A) | **3** (Grade A) | **40% reduction**: In-memory balance & expense summation loops delegated to SQL aggregations. |
| `DashboardView._draw_chart` | **5** (Grade A) | **3** (Grade A) | **40% reduction**: Chart data pre-aggregated in repository, removing UI data-munging loops. |
| `LoginFrame.login` | **4** (Grade A) | **2** (Grade A) | **50% reduction**: Field validation and error dispatching encapsulated inside `AuthController`. |
| `LoginFrame.register` | **4** (Grade A) | **2** (Grade A) | **50% reduction**: Password hashing checks and exception handling delegated to `AuthController`. |
| `BudgetView.save_budget` | **3** (Grade A) | **2** (Grade A) | **33% reduction**: Threshold range validation and entity upsert logic cleanly delegated. |
| `TransactionService.add_transaction` | **7** (Grade B) | **6** (Grade B) | **O(N) loop eliminated**: Python date-parsing scan replaced with 1 direct SQL query. |
| **Total Analyzed Blocks** | 62 blocks | 150 blocks | Codebase grew with modular controllers & repositories, maintaining an overall **Grade A** (2.55 average). |

---

### Metric 2: Maintainability Index (MI)
| Module / File | Baseline MI | Evolved MI | Change | Interpretation |
|---|---|---|---|---|
| `src/services/transaction_service.py` | 49.24 (Grade A) | **65.94** (Grade A) | **+16.70** ⬆️ | Rewritten service is significantly cleaner, modular, and easier to maintain. |
| `src/ui/login_frame.py` | 58.59 (Grade A) | **67.13** (Grade A) | **+8.54** ⬆️ | Simplified by delegating logic to `AuthController`. |
| `src/ui/views/dashboard_view.py` | 60.59 (Grade A) | **65.09** (Grade A) | **+4.50** ⬆️ | Simplified by consuming pre-aggregated controller results. |
| `src/controllers/auth_controller.py` | *(new)* | **76.52** (Grade A) | Clean | Highly maintainable, decoupled controller. |
| `src/controllers/budget_controller.py` | *(new)* | **67.53** (Grade A) | Clean | Strong separation of concerns. |
| `src/controllers/transaction_controller.py`| *(new)* | **61.29** (Grade A) | Clean | Decouples UI from data manipulation. |
| `src/repositories/user_repository.py` | *(new)* | **100.00** (Grade A) | Perfect | Pure SQL persistence with zero business logic. |
| `src/repositories/base_repository.py` | *(new)* | **100.00** (Grade A) | Perfect | Modular connection provider. |

---

### Metric 3: Automated Test Coverage
| Layer | Baseline Tested Statements | Evolved Tested Statements | Evolved Coverage |
|---|---|---|---|
| **Core & Result DTOs** | 0 stmts | 41 stmts | **90%** |
| **Controllers Layer** | 0 stmts | 173 stmts | **74%** |
| **Services Layer** | 84 stmts | 216 stmts | **87%** |
| **Repositories Layer** | 0 stmts | 180 stmts | **76%** |
| **Migrations Layer** | 0 stmts | 91 stmts | **87%** |
| **Test Suites** | 54 stmts | 377 stmts | **98%** |
| **Total Test Suite** | 256 stmts (3 tests) | **1,166 stmts (16 tests)** | **86% Total Coverage** |

---

## 2. Concise Change Log

| Version / Tag | Component / File Affected | Change Category | Description & Justification |
|---|---|---|---|
| `v2.0.0-mig-01` | `src/core/config.py` | **Migration (Part A)** | Externalized configuration for database paths, security iterations, supported currencies, and payment methods. |
| `v2.0.0-mig-02` | `src/data/migrations/` | **Migration (Part A)** | Implemented `MigrationManager` and versioned SQL scripts (`001_baseline_schema.sql`, `002_add_payment_methods_and_tags.sql`). |
| `v2.0.0-ref-01` | `src/repositories/` | **Refactoring (Part B)** | Implemented `BaseRepository`, `UserRepository`, `TransactionRepository`, and `BudgetRepository` to isolate all SQL access. |
| `v2.0.0-ref-02` | `src/controllers/` | **Refactoring (Part B)** | Implemented `BaseController` (with `Result` wrapper), `AuthController`, `TransactionController`, and `BudgetController`. |
| `v2.0.0-ref-03` | `src/ui/` | **Refactoring (Part B)** | Refactored `LoginFrame`, `DashboardView`, `TransactionView`, and `BudgetView` to communicate exclusively via controllers. |
| `v2.0.0-rew-01` | `src/services/transaction_service.py` | **Rewriting (Part C)** | Rewrote `TransactionService` to eliminate $O(N)$ in-memory linear scans and date parsing in favor of SQL aggregations. |
| `v2.0.0-rew-02` | `src/services/csv_service.py` | **Rewriting (Part C)** | Rewrote `CSVService` to replace silent exception swallowing with strict header validation, atomic batching, and `ImportResult`. |
| `v2.0.0-tst-01` | `tests/` | **Testing (Quality)** | Added `test_controllers.py`, `test_rewritten_classes.py`, `test_migration.py`, and 5 end-to-end integration workflows (`test_integration.py`). |

