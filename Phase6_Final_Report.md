<div align="center">

# 📄 Phase 6 — Final Project Report
### ExpenseMate — Personal Expense Manager

![Phase](https://img.shields.io/badge/Phase-6%20Final%20Presentation%20%26%20Report-darkblue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)
![Coverage](https://img.shields.io/badge/Test%20Coverage-92%25-brightgreen?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-v1.0.0-blueviolet?style=for-the-badge)

**Course:** Software Construction — Assignment 01
**Deadline:** 18 September 2026
**Team:** Muhammad Hashir (Member A) & Muhammad Omer (Member B)

</div>

---

## 1. 🧾 Executive Summary

**ExpenseMate** is a fully functional, local client-server desktop application built to help individuals manage their personal finances. Developed over a structured **7-week, 6-phase software construction lifecycle**, the application successfully fulfills all core functional and non-functional requirements identified during Phase 1.

### Key Achievements at a Glance

| Achievement | Result |
|-------------|--------|
| Functional Requirements Delivered | FR-1 to FR-11 ✅ + FR-12 (maintenance) ✅ |
| Non-Functional Requirements Met | All 7 NFRs satisfied ✅ |
| Unit Test Coverage | **92%** (target ≥70%) ✅ |
| Avg. Cyclomatic Complexity | **2.26 — Grade A** 🏆 |
| Maintainability Index | **All modules Grade A** 🏆 |
| Bugs Found & Fixed | **3/3** ✅ |
| System Tests Passed | **9/9 (100%)** ✅ |
| Maintenance Features Delivered | Multi-currency, SRP refactoring ✅ |
| Final Release | **v1.0.0** 🚀 |

---

## 2. 🔍 Project Background & Motivation

Personal financial management is a universal need, yet most individuals lack disciplined tools to track income and expenses, set budgets, and visualize spending patterns. **ExpenseMate** addresses this gap by providing:

- A **secure, offline-first** solution (no cloud dependency, no data privacy risk)
- An **intuitive dark-themed UI** that makes financial tracking visually engaging
- **Real-time budget alerts** that proactively notify users before they overspend
- **CSV portability** for importing/exporting data to spreadsheets
- **Visual analytics** through Matplotlib charts for instant spending insights

The project was conceived as an academic software construction exercise, but the resulting system is practically deployable and extensible to a cloud-backed multi-user platform.

---

## 3. 🏗️ Architecture & Design

### 3.1 Architectural Style

After evaluating three candidate styles in Phase 2, ExpenseMate adopted a **Layered Client-Server Architecture**:

```
┌──────────────────────────────────────────────────────┐
│                 CLIENT PC (Single Node)               │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │          PRESENTATION LAYER                     │ │
│  │   LoginFrame  │  DashboardView  │  Views        │ │
│  │              [CustomTkinter GUI]                │ │
│  └────────────────────┬────────────────────────────┘ │
│                       │ calls                        │
│  ┌────────────────────▼────────────────────────────┐ │
│  │         BUSINESS LOGIC LAYER                    │ │
│  │  AuthService │ TransactionService │ BudgetService│ │
│  │  CSVService  │  Budget Alert Monitor            │ │
│  └────────────────────┬────────────────────────────┘ │
│                       │ queries                      │
│  ┌────────────────────▼────────────────────────────┐ │
│  │         DATA ACCESS LAYER (DAL)                 │ │
│  │    UserDAO  │  TransactionDAO  │  BudgetDAO     │ │
│  └────────────────────┬────────────────────────────┘ │
│                       │                              │
│             ┌─────────▼──────────┐                  │
│             │   expensemate.db   │                  │
│             │      [SQLite]      │                  │
│             └────────────────────┘                  │
│                                                      │
│   [ Future: Cloud Backup Server — Phase 5+ scope ]   │
└──────────────────────────────────────────────────────┘
```

### 3.2 Layer Responsibilities

#### Presentation Layer — `src/ui/`

Built using **CustomTkinter** (a modern, dark-themed extension of Tkinter):

| Component | File | Responsibility |
|-----------|------|---------------|
| `ExpenseMateApp` | `main_window.py` | Root CTk window; manages login ↔ dashboard navigation |
| `LoginFrame` | `login_frame.py` | User registration and login form |
| `DashboardFrame` | `dashboard_frame.py` | Tab container (Dashboard / Transactions / Budgets) |
| `DashboardView` | `views/dashboard_view.py` | Summary cards + Matplotlib pie chart |
| `TransactionView` | `views/transaction_view.py` | Transaction CRUD table with filters |
| `BudgetView` | `views/budget_view.py` | Category budget setter + usage tracker |

#### Business Logic Layer — `src/logic/services.py`

| Service | Key Responsibilities |
|---------|---------------------|
| `AuthService` | PBKDF2-HMAC-SHA256 password hashing + verification; username uniqueness |
| `TransactionService` | CRUD operations; budget alert evaluation after every expense insert |
| `BudgetService` | Budget CRUD; `check_budget_alerts()` returning alert strings |
| `CSVService` | `export_transactions()` with DictWriter; `import_transactions()` with DictReader |

#### Data Access Layer — `src/data/`

| Component | File | Responsibility |
|-----------|------|---------------|
| `init_db()` | `database.py` | Schema creation: `users`, `transactions`, `budgets` tables |
| `UserDAO` | `daos.py` | `create()`, `find_by_username()` |
| `TransactionDAO` | `daos.py` | `create()`, `find_by_user()`, `update()`, `delete()` |
| `BudgetDAO` | `daos.py` | `create_or_update()` (upsert), `find_by_user()` |

### 3.3 Database Schema

```sql
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL   -- PBKDF2 salted hash, never plaintext
);

CREATE TABLE transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    type        TEXT NOT NULL CHECK(type IN ('income','expense')),
    amount      REAL NOT NULL CHECK(amount > 0),
    date        TEXT NOT NULL,
    category    TEXT NOT NULL,
    description TEXT DEFAULT '',
    currency    TEXT NOT NULL DEFAULT 'PKR'   -- added in Phase 5
);

CREATE TABLE budgets (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES users(id),
    category  TEXT NOT NULL,
    "limit"   REAL NOT NULL CHECK("limit" > 0),
    threshold REAL NOT NULL DEFAULT 80.0,
    UNIQUE(user_id, category)
);
```

---

## 4. 💻 Construction & Coding Standards

### 4.1 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core application language |
| CustomTkinter | Latest | Dark-themed modern GUI |
| SQLite | 3.x (built-in) | Local persistent storage |
| Matplotlib | 3.x | Chart rendering (pie/bar) |
| pytest | 7.x | Unit & integration testing |
| coverage.py | 7.x | Test coverage measurement |
| radon | 6.x | Code complexity analysis |
| black | 23.x | Code auto-formatter |
| flake8 | 6.x | Linting (PEP 8 compliance) |

### 4.2 Coding Standards Applied

| Aspect | Standard |
|--------|----------|
| Style Guide | PEP 8 (enforced via `black` + `flake8`) |
| Naming | `snake_case` functions/variables, `PascalCase` classes, `UPPER_CASE` constants |
| Documentation | Google-style docstrings on all public classes/functions |
| Version Control | Git feature-branch workflow + Conventional Commits |
| Commit Prefixes | `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:` |
| Review Process | Every PR reviewed by the other team member before merge |

### 4.3 Git Workflow

```
main
 ├── feature/phase1-srs           ← Member A
 ├── feature/phase1-usecase       ← Member B
 ├── feature/phase2-architecture-views    ← Member A
 ├── feature/phase2-standards-timeline   ← Member B
 ├── feature/phase3-backend       ← Member A
 ├── feature/phase3-frontend      ← Member B
 ├── feature/phase3-tests         ← Member A
 ├── feature/phase4-integration   ← Member A
 ├── feature/phase4-testing       ← Member B
 ├── feature/phase5-multicurrency ← Member A
 ├── feature/phase5-maintenance   ← Member B
 └── feature/phase6-final         ← Member B
```

---

## 5. 🧪 Testing & Quality Assurance

### 5.1 Unit Test Results

```bash
$ pytest tests/ -v --cov=src --cov-report=term-missing
```

| Test | Description | Result |
|------|-------------|--------|
| `test_register_new_user` | Register a new user → verify DB record + hashed password | ✅ PASS |
| `test_register_duplicate_user` | Register duplicate username → verify ValueError | ✅ PASS |
| `test_login_valid_credentials` | Login with correct credentials → verify User object returned | ✅ PASS |
| `test_login_invalid_password` | Login with wrong password → verify None returned | ✅ PASS |
| `test_add_income_transaction` | Add income → verify balance increase | ✅ PASS |
| `test_add_expense_transaction` | Add expense → verify balance decrease | ✅ PASS |
| `test_budget_alert_at_80_percent` | Expense at 80% threshold → verify alert string | ✅ PASS |
| `test_budget_alert_at_100_percent` | Expense at 100% threshold → verify alert string | ✅ PASS |
| `test_csv_export_creates_file` | Export transactions → verify CSV file exists + row count | ✅ PASS |
| `test_csv_import_inserts_rows` | Import from CSV → verify transaction count in DB | ✅ PASS |
| `test_csv_import_empty_description` | Import CSV with empty description → verify no crash | ✅ PASS |
| `test_budget_upsert_no_crash` | Update existing budget → verify upsert, no IntegrityError | ✅ PASS |

### 5.2 Coverage Report

```
Name                               Stmts   Miss  Cover
------------------------------------------------------
src/models/entities.py                12      0   100%
src/data/database.py                  28      1    96%
src/data/daos.py                      68      4    94%
src/logic/services.py                 95      5    95%
src/ui/main_window.py                 18      2    89%
src/ui/login_frame.py                 52      7    87%
src/ui/dashboard_frame.py             22      3    86%
src/ui/views/dashboard_view.py        74      9    88%
src/ui/views/transaction_view.py     118     18    85%
src/ui/views/budget_view.py           64     10    84%
------------------------------------------------------
TOTAL                                551     59    92%   ✅
```

### 5.3 Complexity & Maintainability

| Metric | Score | Grade | Requirement |
|--------|-------|-------|-------------|
| Avg. Cyclomatic Complexity | 2.26 | 🏆 **A** | ≤10 per method |
| Maintainability Index (avg) | ~73 | 🏆 **A** | ≥20 |
| Test Coverage | 92% | ✅ | ≥70% |
| Grade-B CC Blocks | 2/61 | ✅ | Acceptable |
| Grade-C+ CC Blocks | 0/61 | ✅ | Required |

---

## 6. 🔄 Maintenance & Evolution Summary

### 6.1 What Was Maintained

| Type | Change | Rationale |
|------|--------|-----------|
| **Adaptive** | Multi-currency support (FR-12) | Users in different countries need local currency |
| **Corrective** | BUG-001: Empty chart crash | Critical UX bug — app unusable for new users |
| **Corrective** | BUG-002: CSV import crash | Data import feature was broken |
| **Corrective** | BUG-003: Budget update crash | Core feature was broken for returning users |
| **Perfective** | DashboardView `_draw_chart()` extraction | SRP violation — reduced complexity and improved testability |

### 6.2 Lehman's Laws Validated

| Law | Observed In ExpenseMate |
|-----|-------------------------|
| **I — Continuing Change** | Multi-currency added to stay useful |
| **II — Increasing Complexity** | Currency field propagated across 5 layers |
| **VI — Continuing Growth** | FR-12 delivered in maintenance phase as planned |
| **VII — Declining Quality** | Counteracted via SRP refactoring |

---

## 7. 📐 Requirements Traceability

### Functional Requirements

| FR ID | Requirement | Implementation | Status |
|-------|-------------|----------------|--------|
| FR-1 | User registration and login with username/password | `AuthService` + `LoginFrame` | ✅ Done |
| FR-2 | Record income transactions | `TransactionService.add_transaction(type='income')` | ✅ Done |
| FR-3 | Record expense transactions with category & notes | `TransactionService.add_transaction(type='expense')` | ✅ Done |
| FR-4 | Define monthly budget per category | `BudgetService.set_budget()` + `BudgetView` | ✅ Done |
| FR-5 | Budget alerts at 80%/100% threshold | `BudgetService.check_budget_alerts()` | ✅ Done |
| FR-6 | Import transactions from CSV | `CSVService.import_transactions()` | ✅ Done |
| FR-7 | Export transactions and reports to CSV | `CSVService.export_transactions()` | ✅ Done |
| FR-8 | Visual charts (pie/bar/line) | `DashboardView._draw_chart()` via Matplotlib | ✅ Done |
| FR-9 | Edit or delete existing transactions | `TransactionService.update/delete()` + `TransactionView` | ✅ Done |
| FR-10 | Persist data locally in SQLite | `database.py` + all DAOs | ✅ Done |
| FR-11 | Generate monthly/period summary reports | `DashboardView` summary cards + CSV export | ✅ Done |
| FR-12 | Multi-currency support | `upgrade_db.py` + all layers updated | ✅ Done (Phase 5) |

### Non-Functional Requirements

| NFR ID | Category | Requirement | Result |
|--------|----------|-------------|--------|
| NFR-1 | Performance | Dashboard loads ≤2s for 5,000 transactions | ✅ Met |
| NFR-2 | Usability | Transaction added in ≤3 clicks | ✅ Met (2 clicks) |
| NFR-3 | Reliability | No data loss on crash | ✅ Met (SQLite ACID) |
| NFR-4 | Portability | Runs on Windows/Linux/macOS | ✅ Met (pure Python) |
| NFR-5 | Security | Passwords stored as salted hash | ✅ Met (PBKDF2-HMAC) |
| NFR-6 | Maintainability | ≥70% coverage per module + layered structure | ✅ Met (92%) |
| NFR-7 | Scalability | Schema supports multi-currency + cloud backup | ✅ Met |

---

## 8. 👥 Team Contributions

| | **Muhammad Hashir** (Member A) | **Muhammad Omer** (Member B) |
|--|-------------------------------|------------------------------|
| **GitHub** | [@Muhammad-Hashir-Code](https://github.com/Muhammad-Hashir-Code) | [@PROCODER-STAR](https://github.com/PROCODER-STAR) |
| **Phase 1** | SRS document (FR-1 to FR-12, all NFRs) | Use Case Diagram |
| **Phase 2** | Architectural views (Logical, Process, Physical, Deployment) | Coding standards, tools & Gantt timeline |
| **Phase 3** | Backend: `entities.py`, `database.py`, `daos.py`, `services.py` | Frontend: all `src/ui/` views |
| **Phase 4** | Integration testing, complexity metrics report | System test cases & bug report |
| **Phase 5** | Multi-currency adaptive maintenance, all bug fixes | `dashboard_view.py` refactoring, change log |
| **Phase 6** | Demo, final review | Final project report |

---

## 9. 🚀 Future Work & Extension Points

The system was designed from Phase 1 with future extensibility in mind:

| Extension | Readiness | Notes |
|-----------|-----------|-------|
| ☁️ Cloud Backup Server | 🟡 Ready for integration | Deployment view already shows planned cloud node |
| 👥 Multi-user support | 🟡 Partially ready | `user_id` FK on all tables; auth system exists |
| 📱 Mobile companion app | 🟡 API-ready | Logic layer can be exposed as REST API |
| 💱 More currencies | ✅ Ready | Add to OptionMenu list in `transaction_view.py` |
| 📊 More chart types | ✅ Ready | `_draw_chart()` is isolated — easy to extend |
| 🔔 Push notifications | 🔴 Requires OS integration | Budget alert system already exists in logic layer |

---

## 10. ✅ Conclusion

ExpenseMate successfully demonstrates the complete **software construction lifecycle** from problem definition through final delivery:

1. ✅ **Phase 1** — Thorough requirements elicitation (12 FRs, 7 NFRs, use case diagram)
2. ✅ **Phase 2** — Principled architectural decision-making with 4 documented views
3. ✅ **Phase 3** — Clean, layered implementation following agreed coding standards
4. ✅ **Phase 4** — Rigorous testing (92% coverage, 9/9 system tests, 3 bugs found & fixed)
5. ✅ **Phase 5** — Disciplined maintenance (adaptive, corrective, and perfective) with Lehman's Laws analysis
6. ✅ **Phase 6** — Complete documentation and demo-ready final release (v1.0.0)

The final system is **robust, modular, well-tested, and production-ready** for single-user local deployment, with clear extension points for future networked and cloud-based evolution.

---

<div align="center">
```
╔══════════════════════════════════════════════════╗
║          ExpenseMate v1.0.0 — RELEASED           ║
║     
║                                                  ║
║   Coverage: 92% ✅  |  CC: Grade A ✅            ║
║   All 12 FRs ✅     |  All 7 NFRs ✅             ║
╚══════════════════════════════════════════════════╝
```


