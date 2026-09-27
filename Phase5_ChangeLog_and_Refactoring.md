<div align="center">

# 🔄 Phase 5 — Maintenance & Evolution Report
### ExpenseMate — Personal Expense Manager

![Phase](https://img.shields.io/badge/Phase-5%20Maintenance%20%26%20Evolution-blueviolet?style=for-the-badge)
![Adaptive](https://img.shields.io/badge/Adaptive-Multi--Currency%20Added-blue?style=for-the-badge)
![Corrective](https://img.shields.io/badge/Corrective-3%20Bugs%20Fixed-red?style=for-the-badge)
![Perfective](https://img.shields.io/badge/Perfective-SRP%20Refactoring-orange?style=for-the-badge)

</div>

---

## 1. 📌 Overview

Phase 5 covers the **Maintenance & Evolution** of ExpenseMate following successful Phase 4 integration and system testing. This phase applies three categories of software maintenance as defined by Lientz & Swanson (1978):

| Maintenance Type | Description | Applied In ExpenseMate |
|-----------------|-------------|------------------------|
| **Adaptive** | Modify system to work in changed environments or add new features | ✅ Multi-currency support |
| **Corrective** | Fix faults found during testing or operation | ✅ BUG-001, BUG-002, BUG-003 |
| **Perfective** | Improve performance, readability, or maintainability | ✅ `dashboard_view.py` refactoring |

---

## 2. 📝 Change Log

| Date | Version | Type | Description | Files Modified | Author |
|------|---------|------|-------------|----------------|--------|
| 2026-09-27 | v0.5.0 | 🔵 Adaptive | **Multi-Currency Support** — Added `currency` field to transaction model; updated DB, DAO, Service, and UI | `upgrade_db.py`, `entities.py`, `daos.py`, `services.py`, `transaction_view.py` | Member A |
| 2026-09-27 | v0.5.1 | 🔴 Corrective | **BUG-001 Fix** — Matplotlib empty chart crash on new account | `dashboard_view.py` | Member A |
| 2026-09-27 | v0.5.1 | 🔴 Corrective | **BUG-002 Fix** — CSV import crash on empty description column | `services.py` | Member A |
| 2026-09-27 | v0.5.1 | 🔴 Corrective | **BUG-003 Fix** — Budget duplicate key SQL crash | `daos.py` | Member A |
| 2026-09-27 | v0.5.2 | 🟠 Perfective | **Refactoring** — Extract `_draw_chart()` from `refresh_data()` in DashboardView | `dashboard_view.py` | Member B |
| 2026-09-27 | v1.0.0 | 🚀 Release | **Final Release** — All phases complete, system stable | All | Both |

---

## 3. 🌍 Adaptive Maintenance — Multi-Currency Feature

### Business Requirement

The original Phase 1 SRS identified **FR-12** as a low-priority maintenance-phase feature:

> *"The system shall support multiple currencies for transaction entry."*

Phase 5 implements FR-12 as an **adaptive maintenance** item.

### Supported Currencies

| Currency | Code | Symbol |
|----------|------|--------|
| Pakistani Rupee | `PKR` | ₨ |
| US Dollar | `USD` | $ |
| Euro | `EUR` | € |
| British Pound | `GBP` | £ |
| Indian Rupee | `INR` | ₹ |

### Implementation — Layer by Layer

The currency field was propagated through all 4 layers of the architecture:

#### Layer 1 — Database (`upgrade_db.py`)

A new migration script was created to add the `currency` column **non-destructively** (preserving all existing data):

```python
# upgrade_db.py
import sqlite3

def upgrade():
    conn = sqlite3.connect("expensemate.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "ALTER TABLE transactions ADD COLUMN currency TEXT NOT NULL DEFAULT 'PKR'"
        )
        conn.commit()
        print("✅ Database upgraded: 'currency' column added to transactions.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Column 'currency' already exists. No upgrade needed.")
        else:
            raise
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
```

> **Key design decision:** Using `DEFAULT 'PKR'` ensures all existing transactions are backward-compatible after migration.

#### Layer 2 — Model (`src/models/entities.py`)

```python
# Before (Phase 3):
@dataclass
class Transaction:
    id: int
    user_id: int
    type: str        # 'income' or 'expense'
    amount: float
    date: str
    category: str
    description: str

# After (Phase 5):
@dataclass
class Transaction:
    id: int
    user_id: int
    type: str
    amount: float
    date: str
    category: str
    description: str
    currency: str = 'PKR'   # ← NEW FIELD (default for backward compat)
```

#### Layer 3 — DAO (`src/data/daos.py`)

```python
# TransactionDAO.create() — updated INSERT
cursor.execute(
    """INSERT INTO transactions
       (user_id, type, amount, date, category, description, currency)
       VALUES (?, ?, ?, ?, ?, ?, ?)""",
    (t.user_id, t.type, t.amount, t.date, t.category, t.description, t.currency)
)

# TransactionDAO.find_by_user() — updated SELECT
cursor.execute(
    "SELECT id, user_id, type, amount, date, category, description, currency
     FROM transactions WHERE user_id = ? ORDER BY date DESC",
    (user_id,)
)
```

#### Layer 4 — Service (`src/logic/services.py`)

```python
# TransactionService.add_transaction() — updated signature
def add_transaction(self, user_id, tx_type, amount, date,
                    category, description, currency='PKR'):
    transaction = Transaction(
        id=None, user_id=user_id, type=tx_type,
        amount=float(amount), date=date, category=category,
        description=description, currency=currency
    )
    self.transaction_dao.create(transaction)
    # ... budget alert check ...
```

#### Layer 5 — UI (`src/ui/views/transaction_view.py`)

Added a **currency dropdown** (OptionMenu) to the Add/Edit transaction form:

```python
# Currency selector in TransactionView
self.currency_var = ctk.StringVar(value="PKR")
self.currency_menu = ctk.CTkOptionMenu(
    form_frame,
    variable=self.currency_var,
    values=["PKR", "USD", "EUR", "GBP", "INR"],
    width=120
)
self.currency_menu.grid(row=5, column=1, padx=10, pady=5, sticky="w")
```

### Impact Assessment

| Layer | Changes Required | Backward Compatible? |
|-------|-----------------|---------------------|
| Database | `ALTER TABLE` migration | ✅ Yes — default value set |
| Model | Added `currency` field | ✅ Yes — default = `'PKR'` |
| DAO | Updated INSERT/SELECT | ✅ Yes |
| Service | Updated method signature | ✅ Yes — default param |
| UI | Added currency OptionMenu | ✅ Yes |

---

## 4. 🔴 Corrective Maintenance — Bug Fixes

All 3 bugs discovered in Phase 4 were patched in Phase 5. See the full root-cause analysis and fix details in [Phase4_TestCases_BugReport.md](Phase4_TestCases_BugReport.md).

| Bug | Description | Fix |
|-----|-------------|-----|
| **BUG-001** | Matplotlib crash on empty chart | Early-return guard + placeholder text |
| **BUG-002** | CSV import crash on empty description | `row.get('Description', '')` fallback |
| **BUG-003** | Budget duplicate key SQL crash | `ON CONFLICT DO UPDATE` upsert |

---

## 5. 🟠 Perfective Maintenance — Refactoring Report

### Target: `DashboardView.refresh_data()` in `dashboard_view.py`

#### Before Refactoring — The Problem

The `refresh_data()` method was a **35+ line monolithic function** with 3 distinct responsibilities mixed together:

```python
# BEFORE — single overloaded method (simplified):
def refresh_data(self):
    # Responsibility 1: Query database
    transactions = self.tx_service.get_transactions(self.user.id)

    # Responsibility 2: Update summary cards (StringVars)
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    self.balance_var.set(f"₨ {total_income - total_expense:,.2f}")
    self.income_var.set(f"₨ {total_income:,.2f}")
    self.expense_var.set(f"₨ {total_expense:,.2f}")

    # Responsibility 3: Build entire Matplotlib figure inline (15+ lines)
    expenses_by_cat = {}
    for t in transactions:
        if t.type == 'expense':
            expenses_by_cat[t.category] = expenses_by_cat.get(t.category, 0) + t.amount
    self.figure.clear()
    ax = self.figure.add_subplot(111)
    # ... 10 more lines of matplotlib setup ...
    self.canvas.draw()
```

**Problems identified:**
- Violated **Single Responsibility Principle (SRP)** — one method doing 3 jobs
- High cyclomatic complexity (**Grade B**)
- Difficult to unit test chart rendering in isolation
- Adding future chart types would make the method even larger

#### After Refactoring — The Solution

Chart rendering logic was extracted into a **private helper method `_draw_chart()`**:

```python
# AFTER — responsibilities separated:
def refresh_data(self):
    """Orchestrates data fetch and UI update. Single responsibility."""
    transactions = self.tx_service.get_transactions(self.user.id)

    # Update summary cards only
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    self.balance_var.set(f"₨ {total_income - total_expense:,.2f}")
    self.income_var.set(f"₨ {total_income:,.2f}")
    self.expense_var.set(f"₨ {total_expense:,.2f}")

    # Delegate chart work to dedicated method
    self._draw_chart(transactions)

def _draw_chart(self, txs):
    """Handles all matplotlib chart aggregation and rendering."""
    expenses_by_cat = {}
    for t in txs:
        if t.type == 'expense':
            expenses_by_cat[t.category] = expenses_by_cat.get(t.category, 0) + t.amount

    self.figure.clear()
    ax = self.figure.add_subplot(111)
    ax.set_facecolor('#2b2b2b')
    self.figure.patch.set_facecolor('#2b2b2b')

    if not expenses_by_cat:
        ax.text(0.5, 0.5, 'No expense data yet.',
                ha='center', va='center', color='gray', fontsize=11)
    else:
        labels = list(expenses_by_cat.keys())
        sizes  = list(expenses_by_cat.values())
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

    self.canvas.draw()
```

#### Refactoring Impact

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| `refresh_data()` lines | ~35 | ~12 | ⬇️ 66% reduction |
| `refresh_data()` CC | 6 (Grade B) | 2 (Grade A) | ✅ Improved |
| `_draw_chart()` CC | — | 3 (Grade A) | ✅ Clean |
| SRP compliance | ❌ Violated | ✅ Compliant | ✅ Fixed |
| Testability | Low | High | ✅ Improved |

---

## 6. ⚖️ Lehman's Laws Analysis

Manny Lehman's laws of software evolution describe how software systems change over time. Applied to ExpenseMate's Phase 5:

### Law I — Continuing Change
> *"A software system must be continually adapted, or it becomes progressively less satisfactory."*

**Applied:** ExpenseMate required adaptive maintenance (multi-currency) to remain useful in a world with multiple currency users. Without this change, the system would have been unsatisfactory for non-PKR users.

### Law II — Increasing Complexity
> *"As a software system evolves, its complexity increases unless work is done to maintain or reduce it."*

**Applied:** Adding the `currency` parameter across 5 layers (DB → Model → DAO → Service → UI) **increased structural complexity**. This validates Lehman's law — evolution always adds entropy.

### Law IV — Conservation of Organizational Stability
> *"The average effective global activity rate on an evolving system is invariant over the product's lifetime."*

**Applied:** Phase 5 changes were scoped and delivered within the planned maintenance window (1 week), consistent with steady-state development velocity.

### Law VI — Continuing Growth
> *"Functional content of a system must be continually increased to maintain user satisfaction over its lifetime."*

**Applied:** FR-12 (multi-currency) was delivered in Phase 5 as planned in Phase 1, demonstrating controlled, planned growth aligned with initial requirements.

### Law VII — Declining Quality
> *"The quality of a software system will appear to be declining unless it is rigorously maintained and adapted."*

**Applied:** Without the perfective maintenance refactoring of `dashboard_view.py`, the codebase quality would have declined as more and more logic was crammed into `refresh_data()`. The refactoring directly counteracts this law.

---

## 7. ✅ Conclusion

Phase 5 successfully applied all three maintenance types to ExpenseMate:

- ✅ **Adaptive:** Multi-currency feature implemented cleanly across all 5 architecture layers with zero data loss
- ✅ **Corrective:** All 3 Phase 4 bugs resolved with targeted, minimal-impact fixes
- ✅ **Perfective:** `dashboard_view.py` refactored to comply with SRP, reducing complexity from Grade B to Grade A


---


