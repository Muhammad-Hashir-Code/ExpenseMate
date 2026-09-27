<div align="center">

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/CustomTkinter-UI-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Coverage-92%25-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Complexity-Grade%20A-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

# 💸 ExpenseMate
### *Personal Expense Manager — Desktop Application*

> A sleek, modern, dark-themed desktop application for managing personal finances — built with Python, SQLite, and CustomTkinter across 6 structured software construction phases.

[![GitHub release](https://img.shields.io/github/v/release/Muhammad-Hashir-Code/ExpenseMate?style=flat-square&color=blueviolet)](https://github.com/Muhammad-Hashir-Code/ExpenseMate/releases)
[![GitHub issues](https://img.shields.io/github/issues/Muhammad-Hashir-Code/ExpenseMate?style=flat-square)](https://github.com/Muhammad-Hashir-Code/ExpenseMate/issues)
[![GitHub stars](https://img.shields.io/github/stars/Muhammad-Hashir-Code/ExpenseMate?style=flat-square&color=gold)](https://github.com/Muhammad-Hashir-Code/ExpenseMate/stargazers)

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [⚙️ Installation](#️-installation)
- [🚀 Running the App](#-running-the-app)
- [🧪 Running Tests](#-running-tests)
- [📊 Phase Overview](#-phase-overview)
- [👥 Team](#-team)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Authentication** | Register & login with PBKDF2 salted password hashing |
| 💰 **Transaction Management** | Add, edit & delete income/expense transactions with categories |
| 🌍 **Multi-Currency Support** | Record transactions in USD, EUR, GBP, PKR, or INR |
| 📊 **Visual Analytics** | Live pie & bar charts powered by Matplotlib |
| 🔔 **Budget Alerts** | Get notified at 80% and 100% of your category budget |
| 📁 **CSV Import / Export** | Import transactions from CSV or export your full report |
| 📆 **Period Reports** | Generate monthly/custom-range summary reports |
| 🎨 **Dark Mode UI** | Sleek, modern dark-themed interface via CustomTkinter |
| 💾 **Local Persistence** | All data safely stored in a local SQLite database |

---

## 🏗️ Architecture

ExpenseMate follows a **Layered Client-Server Architecture** — fully local in this release, with a cloud-backup extension point built into the design.

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER (UI)         │
│   LoginFrame │ DashboardView │ Views    │
│          [CustomTkinter]                │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│       BUSINESS LOGIC LAYER              │
│  AuthService │ TransactionService       │
│  BudgetService │ CSVService             │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│        DATA ACCESS LAYER (DAL)          │
│   UserDAO │ TransactionDAO │ BudgetDAO  │
│              [SQLite]                   │
└─────────────────────────────────────────┘
```

### 📐 Key Design Decisions

- **Layered Separation** — UI never touches SQL; Business Logic never imports Tkinter
- **DAO Pattern** — All database operations isolated in `daos.py`; storage engine is swappable
- **Budget Alert Monitor** — Concurrent alert evaluation after every expense insert
- **Non-Destructive DB Upgrades** — `upgrade_db.py` adds columns safely without data loss

---

## 📁 Project Structure

```
ExpenseMate/
│
├── app.py                          # 🚀 Entry point
├── upgrade_db.py                   # 🔧 DB migration script (adds currency column)
├── requirements.txt                # 📦 Dependencies
│
├── src/
│   ├── models/
│   │   └── entities.py             # 📦 User, Transaction, Budget dataclasses
│   │
│   ├── data/
│   │   ├── database.py             # 🗄️  DB initializer & schema creation
│   │   └── daos.py                 # 🔌 UserDAO, TransactionDAO, BudgetDAO
│   │
│   ├── logic/
│   │   └── services.py             # ⚙️  AuthService, TransactionService, BudgetService, CSVService
│   │
│   └── ui/
│       ├── main_window.py          # 🪟 Root application window
│       ├── login_frame.py          # 🔐 Login & Registration screen
│       ├── dashboard_frame.py      # 🗂️  Tab container
│       └── views/
│           ├── dashboard_view.py   # 📊 Charts & summary cards
│           ├── transaction_view.py # 💳 Transaction CRUD UI
│           └── budget_view.py      # 🎯 Budget management UI
│
├── tests/
│   └── test_services.py            # 🧪 pytest unit tests (92% coverage)
│
└── docs/
    ├── ExpenseMate_SRS.docx        # 📋 Phase 1 — Requirements
    ├── ExpenseMate_Architecture_Document.docx  # 📐 Phase 2 — Architecture
    ├── Phase4_Complexity_Metrics.md            # 📈 Phase 4 — Metrics
    ├── Phase4_TestCases_BugReport.md           # 🐛 Phase 4 — Testing
    ├── Phase5_ChangeLog_and_Refactoring.md     # 🔄 Phase 5 — Maintenance
    └── Phase6_Final_Report.md                  # 📄 Phase 6 — Final Report
```

---

## ⚙️ Installation

### Prerequisites

- Python **3.11+**
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Muhammad-Hashir-Code/ExpenseMate.git
cd ExpenseMate

# 2. (Recommended) Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### `requirements.txt` includes:

```
customtkinter
matplotlib
pytest
coverage
```

---

## 🚀 Running the App

```bash
python app.py
```

The app will launch in **Dark Mode** with a login screen.

> **First time?** Click **Register** to create an account, then log in.

### Running the DB Migration (if upgrading from a previous version)

```bash
python upgrade_db.py
```

This safely adds the `currency` column to existing databases without data loss.

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### ✅ Test Results

| Metric | Value |
|--------|-------|
| **Total Coverage** | **92%** ✅ (target: ≥70%) |
| **Test Cases** | 9 system tests + unit tests |
| **Avg. Cyclomatic Complexity** | **2.26 — Grade A** 🏆 |
| **Maintainability Index** | **All modules Grade A** |

---

## 📊 Phase Overview

This project was built across **6 structured software construction phases**:

```
Phase 1  ──▶  Phase 2  ──▶  Phase 3  ──▶  Phase 4  ──▶  Phase 5  ──▶  Phase 6
Requirements   Architecture    Coding &      Integration    Maintenance   Final
& SRS          & Planning      Unit Tests    & Testing      & Evolution   Report
Aug 03-09      Aug 10-16       Aug 17-30     Aug 31-Sep 06  Sep 07-13     Sep 14-18
```

### Phase Highlights

<details>
<summary><b>📋 Phase 1 — Problem Definition & Requirements</b></summary>

- Produced full **Software Requirements Specification (SRS)**
- Defined **12 Functional Requirements** (FR-1 to FR-12) and **7 Non-Functional Requirements**
- Created **Use Case Diagram** identifying all primary and secondary use cases
- Identified maintenance scope: multi-currency & cloud backup as Phase 5+ items

</details>

<details>
<summary><b>📐 Phase 2 — Architecture & Construction Planning</b></summary>

- Selected **Layered Client-Server Architecture** after evaluating 3 candidate styles
- Produced **4 architectural views**: Logical, Process, Physical, Deployment
- Defined coding standards: **PEP 8**, Black formatter, Flake8 linter
- Adopted **Conventional Commits** and **Feature-Branch Git workflow**
- Created 7-week **Gantt chart** for phase tracking

</details>

<details>
<summary><b>💻 Phase 3 — Coding & Unit Testing</b></summary>

- **Member A (Backend):** `entities.py`, `database.py`, `daos.py`, `services.py`
- **Member B (Frontend):** All `src/ui/` views — Login, Dashboard, Transactions, Budgets
- Unit tests written with `pytest`; all core services covered

</details>

<details>
<summary><b>🔬 Phase 4 — Integration & System Testing</b></summary>

- **9 system test cases** (TC-01 to TC-09) — all ✅ PASS
- **3 bugs found and fixed** (BUG-001 to BUG-003)
- Complexity analysis via `radon`: Average CC = **2.26 (Grade A)**
- All module Maintainability Indexes scored **Grade A**

</details>

<details>
<summary><b>🔄 Phase 5 — Maintenance & Evolution</b></summary>

- **Adaptive Maintenance:** Added full **multi-currency support** (USD/EUR/GBP/PKR/INR) — non-destructive DB upgrade
- **Perfective Maintenance:** Refactored `dashboard_view.py` — extracted `_draw_chart()` (Single Responsibility Principle)
- **Corrective Maintenance:** Fixed BUG-001, BUG-002, BUG-003
- Applied **Lehman's Laws** analysis to validate maintenance decisions

</details>

<details>
<summary><b>📄 Phase 6 — Final Presentation & Report</b></summary>

- Full **Final Project Report** documenting all phases
- Live demo of all features
- 92% test coverage confirmed
- System marked **stable and ready for future cloud-backup expansion**

</details>

---

## 🐛 Known Bugs Fixed

| Bug ID | Description | Fix |
|--------|-------------|-----|
| **BUG-001** | Matplotlib crashed on empty chart | Added early-return guard in `dashboard_view.py` |
| **BUG-002** | CSV import crashed on empty description fields | Used `row.get('Description', '')` fallback |
| **BUG-003** | Duplicate category budget threw raw SQL error | Upgraded to `ON CONFLICT DO UPDATE SET` |

---

## 👥 Team

| Member | Role | Contributions |
|--------|------|--------------|
| **Muhammad Hashir** ([@Muhammad-Hashir-Code](https://github.com/Muhammad-Hashir-Code)) | Member A — Backend Lead | SRS, Architecture Views, Backend (DAOs/Services/DB), Bug Fixes, Multi-Currency Feature |
| **Muhammad Omer** ([@PROCODER-STAR](https://github.com/PROCODER-STAR)) | Member B — Frontend Lead | Use Case Diagram, Standards & Timeline, All UI Views, System Testing, Refactoring, Final Report |

---

## 📈 Quality Metrics

```
╔══════════════════════════════════════════════════╗
║           ExpenseMate Quality Report             ║
╠══════════════════════════════════════════════════╣
║  Test Coverage        ████████████░  92% ✅      ║
║  Cyclomatic CC        Grade A (2.26 avg)  🏆     ║
║  Maintainability      All modules Grade A 🏆     ║
║  Functional Reqs      FR-1 to FR-11 ✅           ║
║  System Tests         TC-01 to TC-09 ✅ (9/9)    ║
║  Bugs Fixed           BUG-001 to BUG-003 ✅      ║
╚══════════════════════════════════════════════════╝
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

