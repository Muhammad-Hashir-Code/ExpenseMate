# Phase 5 Deliverable: Change Log & Refactoring Report

**Project:** ExpenseMate - Personal Expense Manager
**Phase:** 5 (Maintenance & Evolution)

## 1. Change Log (Adaptive & Corrective Maintenance)

| Date | Type | Description | Files Modified |
|------|------|-------------|----------------|
| 2026-09-27 | Adaptive | **Feature: Multi-Currency Support**. Added a `currency` column to the SQLite database and updated the UI forms to allow users to select their transaction currency (USD, EUR, GBP, PKR, INR). | `upgrade_db.py` (new), `entities.py`, `daos.py`, `services.py`, `transaction_view.py` |
| 2026-09-27 | Corrective | Fixed Matplotlib empty chart crash (BUG-001). | `dashboard_view.py` |
| 2026-09-27 | Corrective | Fixed CSV empty description import failure (BUG-002) and Budget unique constraint SQL crash (BUG-003). | `services.py`, `daos.py` |

## 2. Refactoring Report (Perfective Maintenance)

**Target Module:** `src/ui/views/dashboard_view.py`

**Before:** The `refresh_data()` method was 35+ lines long. It had mixed responsibilities: it queried the database, computed sums for the summary cards, updated the Tkinter StringVars, aggregated expenses by category, and built the entire Matplotlib Figure and Canvas hierarchy inline. This violated the Single Responsibility Principle and made the function hard to read and test.

**After:** The chart rendering logic was extracted into a private helper method `_draw_chart(self, txs)`. 
- `refresh_data()` is now strictly responsible for high-level data orchestration and updating text variables.
- `_draw_chart()` focuses entirely on data aggregation for charting and matplotlib rendering.
- **Benefit:** Reduced cyclomatic complexity per method, increased readability, and easier future modification of charting logic.

## 3. Lehman’s Laws Analysis

Applied to ExpenseMate's evolution in Phase 5:
- **Law of Continuing Change:** As dictated by the assignment, ExpenseMate had to adapt (adding Multi-currency) to remain useful in a changing environment, validating this law.
- **Law of Increasing Complexity:** Adding the currency parameter across the `Transaction` entity, `TransactionDAO`, `TransactionService`, and `TransactionView` increased the system's structural complexity.
- **Law of Declining Quality:** Without the refactoring (perfective maintenance) applied to `dashboard_view.py`, the codebase's quality would have declined as more logic was crammed into a single method, validating the need for constant refactoring as systems evolve.
