<div align="center">

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/CustomTkinter-UI-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Coverage-86%25-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Complexity-Grade%20A-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Architecture-4--Layer-orange?style=for-the-badge"/>

# 💸 ExpenseMate (v2.0 — Software Evolution)
### *Personal Expense Manager — Desktop Application*

> A robust, modern, 4-tier desktop application for managing personal finances — evolved through **Database Migration**, **Layered Refactoring**, and **Class Rewriting** according to Software Construction & Development Assignment 02 specifications.

</div>

---

## 🏗️ 4-Layer Architecture

ExpenseMate follows the strict required dependency direction:
$$\text{Controller} \longrightarrow \text{Services} \longrightarrow \text{Repository} \longrightarrow \text{Database}$$

```
┌────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER (UI)                  │
│       LoginFrame │ DashboardView │ Views               │
│                   [CustomTkinter]                      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  CONTROLLER LAYER                      │
│   AuthController │ TransactionController               │
│   BudgetController │ Result[T] DTO Wrapper             │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  SERVICES LAYER                        │
│   AuthService │ BudgetService │ TransactionService     │
│   CSVService (Rewritten with schema validation)        │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                 REPOSITORY LAYER                       │
│   UserRepository │ TransactionRepository               │
│   BudgetRepository │ SQL Aggregations                  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  DATABASE LAYER                        │
│   SQLite Database │ MigrationEngine                    │
│   001_baseline_schema │ 002_add_payment_methods        │
└────────────────────────────────────────────────────────┘
```

---

## ✨ Key Assignment 02 Features & Evolution

1. **Part A — Migration:**
   - Dedicated `MigrationEngine` tracking a `schema_migrations` audit table.
   - Versioned SQL migrations (`001_baseline_schema.sql`, `002_add_payment_methods_and_tags.sql`).
   - Extended schema with `payment_method` (`Cash`, `Credit Card`, `Debit Card`, `Bank Transfer`, `Other`) and `tags`.
   - Externalized configuration in `src/core/config.py`.
   - Zero data loss: existing Assignment 01 data is automatically preserved.
2. **Part B — Layered Architecture Refactoring:**
   - Introduced `Controller` layer (`AuthController`, `TransactionController`, `BudgetController`).
   - Clean `Result[T]` response wrapper isolating presentation from business logic.
   - Isolated SQL execution exclusively inside `Repositories`.
3. **Part C — Rewritten Selected Classes:**
   - **`TransactionService`**: Eliminates $O(N)$ in-memory full table scans and repetitive string-to-date parsing by delegating month-to-date spending directly to repository SQL aggregations.
   - **`CSVService`**: Replaced bare `except: pass` with line-by-line error reporting, strict header verification, and atomic batch ingestion via `create_batch()`.
4. **Testing Suite:**
   - 16 automated tests covering unit tests, migration tests, rewritten class tests, and 5 complete end-to-end integration workflows.
   - 86% total statement coverage.

---

## 🚀 Quickstart & Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python -m src.data.migrations.migration_manager
```

### 3. Launch Application
```bash
python app.py
```

### 4. Run Test Suite
```bash
pytest -v
```

### 5. Check Test Coverage
```bash
python -m coverage run -m pytest tests/
python -m coverage report -m
```

### 6. Analyze Code Metrics
```bash
# Cyclomatic Complexity
python -m radon cc src/ -s -a

# Maintainability Index
python -m radon mi src/ -s
```

---

## 👥 Team
- **Muhammad Hashir (Member A)** — Migration Engine, Config, Controllers, Rewriting CSVService, Documentation.
- **Muhammad Omer (Member B)** — Repositories, Budget Logic, Rewriting TransactionService, Integration Tests.

