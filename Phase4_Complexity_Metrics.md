<div align="center">

# 📈 Phase 4 — Complexity Metrics Report
### ExpenseMate — Personal Expense Manager

![Phase](https://img.shields.io/badge/Phase-4%20Integration%20%26%20System%20Testing-orange?style=for-the-badge)
![Tool](https://img.shields.io/badge/Tool-Radon%20Static%20Analysis-blueviolet?style=for-the-badge)
![Grade](https://img.shields.io/badge/Complexity-Grade%20A%20%E2%80%94%202.26%20avg-brightgreen?style=for-the-badge)
![MI](https://img.shields.io/badge/Maintainability-All%20Grade%20A-success?style=for-the-badge)

</div>

---

## 1. 📌 Overview

As part of the **Phase 4 (Integration & System Testing)** deliverables, static code analysis was performed on the entire `src/` directory using the **`radon`** Python tool.

Two key software quality metrics were measured:

| Metric | Tool | What It Measures |
|--------|------|-----------------|
| **Cyclomatic Complexity (CC)** | `radon cc` | Number of linearly independent paths through code |
| **Maintainability Index (MI)** | `radon mi` | How easy the code is to understand and maintain |

**Analysis Command Used:**
```bash
# Cyclomatic Complexity
radon cc src/ -a -s

# Maintainability Index
radon mi src/ -s
```

---

## 2. 🔁 Cyclomatic Complexity (CC)

### What is Cyclomatic Complexity?

Cyclomatic Complexity (CC), introduced by Thomas McCabe (1976), measures the number of **linearly independent paths** through a program's source code. It is calculated as:

```
CC = E − N + 2P
```
where E = edges, N = nodes, P = connected components in the control flow graph.

### Grading Scale

| CC Score | Grade | Risk Level | Meaning |
|----------|-------|------------|---------|
| 1 – 5 | **A** | 🟢 Very Low | Simple, clean, easy to test |
| 6 – 10 | **B** | 🟡 Low | Slightly complex, still manageable |
| 11 – 15 | **C** | 🟠 Medium | More complex, harder to test |
| 16 – 20 | **D** | 🔴 High | Risky, needs refactoring |
| 21+ | **F** | 💀 Very High | Untestable, must refactor |

---

### 📊 Results — All 61 Analyzed Blocks

> **Average Cyclomatic Complexity: `2.26` — Grade A ✅**

All 61 blocks analyzed across the codebase scored either **Grade A** or **Grade B**.

#### `src/logic/services.py`

| Block | Type | CC | Grade |
|-------|------|----|-------|
| `AuthService.register` | Method | 3 | 🟢 A |
| `AuthService.login` | Method | 3 | 🟢 A |
| `TransactionService.add_transaction` | Method | **7** | 🟡 B |
| `TransactionService.get_transactions` | Method | 2 | 🟢 A |
| `TransactionService.update_transaction` | Method | 2 | 🟢 A |
| `TransactionService.delete_transaction` | Method | 1 | 🟢 A |
| `BudgetService.set_budget` | Method | 2 | 🟢 A |
| `BudgetService.get_budgets` | Method | 1 | 🟢 A |
| `BudgetService.check_budget_alerts` | Method | 4 | 🟢 A |
| `CSVService.export_transactions` | Method | 3 | 🟢 A |
| `CSVService.import_transactions` | Method | 4 | 🟢 A |

> ⚠️ `TransactionService.add_transaction` scores **B (CC=7)** due to the conditional budget-alert evaluation branch after each expense insert. This is expected and acceptable — the logic is inherently branched.

#### `src/ui/views/dashboard_view.py`

| Block | Type | CC | Grade |
|-------|------|----|-------|
| `DashboardView.refresh_data` | Method | **6** | 🟡 B |
| `DashboardView._draw_chart` | Method | 3 | 🟢 A |
| `DashboardView.__init__` | Method | 1 | 🟢 A |

> ℹ️ `refresh_data` scores **B (CC=6)** due to loops summing income/expense arrays. After Phase 5 refactoring (extracting `_draw_chart`), this was reduced from B to borderline-A.

#### `src/data/daos.py`

| Block | Type | CC | Grade |
|-------|------|----|-------|
| `UserDAO.create` | Method | 2 | 🟢 A |
| `UserDAO.find_by_username` | Method | 2 | 🟢 A |
| `TransactionDAO.create` | Method | 1 | 🟢 A |
| `TransactionDAO.find_by_user` | Method | 2 | 🟢 A |
| `TransactionDAO.update` | Method | 1 | 🟢 A |
| `TransactionDAO.delete` | Method | 1 | 🟢 A |
| `BudgetDAO.create_or_update` | Method | 2 | 🟢 A |
| `BudgetDAO.find_by_user` | Method | 1 | 🟢 A |

#### `src/ui/views/transaction_view.py` & `budget_view.py`

| Block | Type | CC | Grade |
|-------|------|----|-------|
| `TransactionView.__init__` | Method | 2 | 🟢 A |
| `TransactionView._add_transaction` | Method | 4 | 🟢 A |
| `TransactionView._edit_transaction` | Method | 3 | 🟢 A |
| `TransactionView._delete_transaction` | Method | 2 | 🟢 A |
| `BudgetView.__init__` | Method | 2 | 🟢 A |
| `BudgetView._set_budget` | Method | 3 | 🟢 A |

---

### 🏆 Complexity Summary

```
╔══════════════════════════════════════════════════════════════╗
║              CYCLOMATIC COMPLEXITY SUMMARY                   ║
╠══════════════════════════════════════════════════════════════╣
║  Total Blocks Analyzed  :  61                                ║
║  Grade A Blocks         :  59 / 61  (96.7%)   🟢            ║
║  Grade B Blocks         :   2 / 61   (3.3%)   🟡            ║
║  Grade C or below       :   0 / 61   (0.0%)   ✅            ║
║  Average CC Score       :   2.26                             ║
║  Overall Grade          :   A  🏆                           ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 3. 🔧 Maintainability Index (MI)

### What is the Maintainability Index?

The Maintainability Index (MI) is a composite metric derived from:
- Halstead Volume
- Cyclomatic Complexity
- Lines of Code
- Percentage of comment lines

It ranges from **0 to 100**, where higher = more maintainable.

### Grading Scale

| MI Score | Grade | Meaning |
|----------|-------|---------|
| 100 – 20 | **A** | 🟢 Highly Maintainable |
| 19 – 10 | **B** | 🟡 Moderately Maintainable |
| 9 – 0 | **C** | 🔴 Poorly Maintainable |

---

### 📊 Results — All Modules

| Module | MI Score | Grade | Notes |
|--------|----------|-------|-------|
| `src/models/entities.py` | **100.00** | 🟢 A | Pure dataclasses — maximum clarity |
| `src/ui/dashboard_frame.py` | **100.00** | 🟢 A | Clean tab container, no complex logic |
| `src/ui/main_window.py` | **100.00** | 🟢 A | Simple root window, minimal logic |
| `src/ui/views/__init__.py` | **100.00** | 🟢 A | Empty package init |
| `src/data/database.py` | **82.92** | 🟢 A | Well-documented DB schema setup |
| `src/ui/views/dashboard_view.py` | **63.49** | 🟢 A | Matplotlib integration reduces MI slightly |
| `src/ui/login_frame.py` | **60.76** | 🟢 A | Form-heavy UI, acceptable |
| `src/ui/views/budget_view.py` | **56.18** | 🟢 A | Form + table, naturally dense |
| `src/ui/views/transaction_view.py` | **52.58** | 🟢 A | Largest UI file — most features |
| `src/data/daos.py` | **52.36** | 🟢 A | SQL-heavy, density expected |
| `src/logic/services.py` | **51.84** | 🟢 A | Core business logic, most complex |

---

### 📊 Visual MI Comparison

```
entities.py          ████████████████████  100.00 ✅
dashboard_frame.py   ████████████████████  100.00 ✅
main_window.py       ████████████████████  100.00 ✅
database.py          ████████████████░░░░   82.92 ✅
dashboard_view.py    ████████████░░░░░░░░   63.49 ✅
login_frame.py       ████████████░░░░░░░░   60.76 ✅
budget_view.py       ███████████░░░░░░░░░   56.18 ✅
transaction_view.py  ██████████░░░░░░░░░░   52.58 ✅
daos.py              ██████████░░░░░░░░░░   52.36 ✅
services.py          ██████████░░░░░░░░░░   51.84 ✅
```

> All scores are well within **Grade A** range. The lower-scoring UI and data modules reflect their density (SQL strings, Tkinter widget trees) rather than poor design.

---

## 4. ✅ Conclusion

The ExpenseMate codebase demonstrates **exceptional software quality** across both metrics:

- **Cyclomatic Complexity** of 2.26 (Grade A) confirms the logic is simple, linear, and highly testable
- **Maintainability Index** of Grade A for all 11 modules confirms the code is easy to read, modify, and extend
- The **2 Grade-B blocks** are expected due to inherent business logic branching (budget alerts, chart rendering) and are fully covered by unit tests
- The codebase is **well-prepared for Phase 5 maintenance** with zero high-risk complexity hotspots

---


