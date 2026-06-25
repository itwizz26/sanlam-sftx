# Solution Design

## 1. Technology Choices
- **Django REST Framework (DRF)**: Chosen for its robust serialization, built-in permission system, and mature API development patterns.
- **PostgreSQL**: Selected over SQLite for production-grade ACID compliance, robust handling of concurrent transactions, and row-level locking capabilities.
- **Docker**: Used to create a reproducible, containerized environment that includes the database, ensuring parity between local development and production environments.

## 2. Data Model & Integrity
- **Account Model**: Designed with a `OneToOne` relationship to the user model. The `balance` is stored as a `DecimalField` to prevent floating-point arithmetic errors common in financial calculations.
- **Transaction Model**: 
    - Designed as an immutable record. 
    - The `ref` field is marked as `unique=True` and indexed (`db_index=True`) to offload duplicate detection to the database engine, ensuring efficiency and data consistency.
- **Audit Logging**: A dedicated `AuditLog` model is implemented to track all transaction attempts, providing an immutable record for debugging batch ingestion failures and business rule rejections.

## 3. Concurrency Strategy
To handle concurrent requests for the same account (a common requirement in loyalty/financial systems):
- **Database Transactions**: All financial operations are wrapped in `transaction.atomic()` to ensure atomicity.
- **Pessimistic Locking**: We utilize `select_for_update()` on the `Account` model. This locks the specific account row upon selection, ensuring that concurrent processes wait in line rather than reading or writing stale balance data.

## 4. Authentication & Access Control
- **Protocol**: Implemented Stateless JWT (JSON Web Tokens) using `djangorestframework-simplejwt`. This avoids server-side session overhead and is ideal for API-first services.
- **Access Model**:
    - **Roles**: Used Django's built-in `Group` and `is_staff` flag to differentiate between `Member` and `Admin`.
    - **Enforcement**: Implemented a custom `IsOwnerOrAdmin` permission class. This encapsulates the logic for data isolation, ensuring a Member cannot access another Member's balance via `GET` or `POST` requests.

## 5. Configuration Management
- **Security**: Eliminated hardcoded secrets (`SECRET_KEY`, `DATABASE_URL`) by migrating to `django-environ`. This ensures that sensitive credentials never enter version control (Git).
- **Environment Parity**: By using `env.db()`, the application dynamically configures its database connection based on the provided URL, allowing the exact same code to run in local Docker containers and production cloud environments without modification.

## 6. AI Implementation Workflow
- **Project Structure**: Adopted the "apps/" pattern for better modularity and separation of concerns between `accounts` (user management) and `wallet` (loyalty logic).
- **Environment**: Defined a `docker-compose.yml` with a `watch` service configuration to enable real-time code synchronization, speeding up the development cycle.