# Comprehensive Solution Design

## 1. Technology Choices
* **Django REST Framework (DRF)**: Chosen for its robust serialization, built-in permission system, and mature API development patterns.
* **PostgreSQL**: Selected for production-grade ACID compliance, robust handling of concurrent transactions, and row-level locking capabilities.
* **Docker**: Used to create a reproducible, containerized environment, ensuring parity between local development and production.
* **JWT (SimpleJWT)**: Implemented for stateless, scalable authentication across distributed service components.

---

## 2. System Architecture & Data Flow
The system follows a decoupled architecture where the **Account** acts as the aggregate root.

* **Registration**: Auto-provisioning via `post_save` signals ensures every user has an `Account` on creation.
* **Transaction Flow**: Requests pass through the `TransactionViewSet`, trigger the `execute_transaction` service, and are committed within a PostgreSQL-locked transaction block.



---

## 3. Concurrency & Integrity
* **Pessimistic Locking**: We use `select_for_update()` to lock account balances during the read-modify-write cycle. This ensures that even under high concurrency, no balance is ever overwritten by stale data.
* **Arithmetic Safety**: We use `DecimalField` to ensure 100% precision for financial point calculations, avoiding the inaccuracies inherent in floating-point math.

---

## 4. Security Model
* **Authentication**: JWT-based stateless authentication.
* **Authorization**:
    * **Admins**: Full access for batch ingestion and global transaction visibility.
    * **Members**: Restricted via `IsOwnerOrAdmin` permissions and `get_queryset` filtering to ensure data isolation.
* **Audit**: Every transaction attempt—success or failure—is recorded in the `AuditLog` with a timestamp and reference, creating a transparent trail for manual ledger reconciliation.

---

## 5. Batch Ingestion Logic
The system implements a fault-tolerant CSV ingestion pipeline:
1.  **Parsing**: Streaming via `csv.DictReader` for efficient memory management.
2.  **Validation**: Every row is checked for type-safety (`Decimal` conversion) and record existence.
3.  **Isolation**: Individual failures (e.g., duplicate reference or insufficient funds) are caught; the system commits successful rows independently and returns a comprehensive error summary.

---

## 6. Development Infrastructure
* **CI/CD Readiness**: `docker-compose` orchestration ensures identical behavior across Dev, Staging, and Production environments.
* **Environment Parity**: Utilizes `django-environ` for secure configuration, ensuring zero hardcoded secrets.
* **Developer Experience**: Configured with Docker volume mapping to enable real-time code synchronization for rapid development cycles.