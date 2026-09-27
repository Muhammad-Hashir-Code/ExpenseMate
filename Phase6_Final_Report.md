# Phase 6 Deliverable: Final Project Report

**Project Title:** ExpenseMate — Personal Expense Manager  
**Course:** Software Construction  
**Team Members:** Member A, Member B  
**Deadline:** 18 September 2026  

---

## 1. Executive Summary
ExpenseMate is a local, client-server desktop application designed to help individuals manage their personal finances. Developed over a 7-week period through six distinct phases of software construction, the application successfully implements all core functional requirements (income/expense tracking, budget alerting, CSV import/export, interactive charting) and non-functional requirements (high usability, fast load times, and transaction safety).

## 2. Architecture & Design
The system was built using a **Layered Client-Server Architecture** operating locally via Python and SQLite.
- **Presentation Layer (UI):** Built using `customtkinter`, this layer provides a sleek, modern, dark-themed interface with intuitive navigation between the Dashboard, Transactions, and Budgets views.
- **Business Logic Layer:** Encapsulated in `services.py`, this layer processes all rules (e.g., PBKDF2 password hashing in `AuthService`, evaluating budget thresholds in `BudgetService`, and managing transactions in `TransactionService`).
- **Data Access Layer (DAL):** Consists of Data Access Objects (`UserDAO`, `TransactionDAO`, `BudgetDAO`) that handle raw SQL execution, ensuring that the Business Logic layer remains agnostic to the underlying storage mechanism.

## 3. Construction & Testing
Following PEP 8 coding standards (enforced via `black` and `flake8`), the codebase was structured for high maintainability.
- **Unit Testing:** The backend modules were rigorously tested using `pytest`. The final coverage report showed **92% total coverage**, significantly exceeding the 70% requirement.
- **Complexity Metrics:** Analysis via `radon` revealed an Average Cyclomatic Complexity of 2.26 (Grade A), indicating that the code is simple, linear, and easy to maintain. The Maintainability Index for all core files averaged over 75 (Grade A).

## 4. Maintenance & Evolution
During Phase 5, the system underwent significant evolution:
- **Adaptive Maintenance:** A multi-currency feature was successfully added, requiring a non-destructive database upgrade and a synchronized update across the Model, DAO, Service, and UI layers.
- **Perfective Maintenance:** The `dashboard_view.py` script was refactored to separate the complex `matplotlib` charting logic from the general UI data refreshing, directly applying Lehman's Law of Declining Quality to keep the codebase healthy.
- **Corrective Maintenance:** Minor faults, such as SQLite unique constraint collisions during budget updates and CSV parsing errors, were identified and patched.

## 5. Conclusion
ExpenseMate successfully applies foundational Software Construction concepts—ranging from requirement elicitation and architectural design to automated testing and software evolution. The final system is robust, modular, and fully prepared for future networked/cloud-based expansion as originally proposed in the deployment view.
