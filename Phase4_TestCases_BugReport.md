# Phase 4 Deliverable: Test Cases & Bug Report

**Project:** ExpenseMate - Personal Expense Manager
**Phase:** 4 (Integration & System Testing)

## 1. System & Integration Test Cases

| Test ID | Module / Component | Description | Expected Result | Status |
|---------|-------------------|-------------|-----------------|--------|
| **TC-01** | `AuthService` | User Registration with valid credentials | User is created in DB and hashed password saved. | ✅ PASS |
| **TC-02** | `AuthService` | Duplicate Registration | System raises a ValueError for existing username. | ✅ PASS |
| **TC-03** | `AuthService` | Login Validation | User is successfully authenticated using salted hash. | ✅ PASS |
| **TC-04** | `BudgetService` | Set Category Budget | Budget constraints (limits and thresholds) saved to DB. | ✅ PASS |
| **TC-05** | `TransactionService` | Add Income | Transaction is saved and balance updates positively. | ✅ PASS |
| **TC-06** | `Integration` | Budget Alert Trigger | Adding an expense that pushes the category total over the threshold % triggers an alert string. | ✅ PASS |
| **TC-07** | `CSVService` | Export to CSV | Generates a valid CSV file containing the user's transactions. | ✅ PASS |
| **TC-08** | `CSVService` | Import from CSV | Parses CSV rows and inserts them via `TransactionService`. | ✅ PASS |
| **TC-09** | `UI Integration` | Dashboard Chart Rendering | Adding an expense updates the Matplotlib pie chart dynamically. | ✅ PASS |

## 2. Fault-Find & Fault-Fix Report

During Phase 3 and early Phase 4 testing, the following faults were identified and resolved:

| Bug ID | Description | Root Cause | Fix Applied | Status |
|--------|-------------|------------|-------------|--------|
| **BUG-001** | UI Chart failed to render when no expenses existed. | The Matplotlib `pie()` function crashed when passed an empty list of sizes. | Added an early return check in `dashboard_view.py` to display a placeholder label if `expenses_by_cat` is empty. | 🛠️ FIXED |
| **BUG-002** | CSV Import crashed on empty description fields. | The `csv.DictReader` returned `None` for missing columns not handled gracefully. | Used `row.get('Description', '')` fallback in `CSVService.import_transactions`. | 🛠️ FIXED |
| **BUG-003** | Duplicate Category Budgets threw raw SQL Errors. | Budget insertions conflicted with the `UNIQUE(user_id, category)` constraint. | Upgraded `BudgetDAO.create_or_update` to use SQLite `ON CONFLICT (...) DO UPDATE SET`. | 🛠️ FIXED |

**Summary:** All known faults discovered during System Testing have been resolved. The system is stable for Phase 5 (Maintenance & Evolution).
