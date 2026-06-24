# Solution Design

## Technology Choices
- **Django REST Framework**: Chosen for its robust serialization and built-in permission system.
- **PostgreSQL**: Used over SQLite for better ACID compliance and concurrency handling.
- **Docker**: Ensures environment consistency and simplifies the "run locally" requirement.

## Concurrency & Integrity
- **Database Transactions**: Used `transaction.atomic` for all financial operations.
- **Pessimistic Locking**: Employed `select_for_update()` to prevent race conditions during balance updates.

## AI Workflow
- Used Gemini to architect the headless DRF structure and enforce separation of concerns via an `apps/` directory pattern.