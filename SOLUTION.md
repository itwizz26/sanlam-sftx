# Comprehensive Solution Design

## 1. Technology Choices
* **Django REST Framework (DRF)**: Chosen for its robust serialization, built-in permission system, and mature API development patterns.
* **PostgreSQL**: Selected for production-grade ACID (Atomicity, Consistency, Isolation, Durability) compliance, robust handling of concurrent transactions, and row-level locking capabilities.
* **Docker**: Used to create a reproducible, containerized environment, ensuring that our local development and production environments match up.
* **JSON Web Token (SimpleJWT)**: Implemented for stateless, scalable authentication across distributed service components.

---

## 2. System Architecture & Data Flow
The system follows a decoupled architecture - meaning that it is organized around the user's **Account**, which acts as the main hub for all related activity.

* **Registration**: Auto-provisioning via `post_save` signals ensures every user has an `Account` on creation.
* **Transaction Flow**: Requests pass through the `TransactionViewSet`, trigger the `execute_transaction` service, and are committed within a PostgreSQL-locked transaction block.

---

## 3. Concurrency & Integrity
* **Pessimistic Locking**: We use `select_for_update()` to lock account balances during the read-modify-write cycle. This ensures that even under high concurrency, no balance is ever overwritten by stale data.
* **Arithmetic Safety**: We use `DecimalField` to ensure 100% precision for `financial point calculations`, avoiding the inaccuracies inherent in floating-point math.

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

## 7. AI-Assisted Development Workflow

This project was developed in close collaboration with an AI assistant ([Aider AI](https://aider.chat/)). This approach accelerated development by automating boilerplate, debugging environment-specific issues, and refining project documentation.


#### Prompt

```
[In the context of the Wallet app] Implement a post_save signal that automatically provisions an Account for every new User.
```

#### What I accepted:
The implementation of a post_save receiver in `apps/wallet/models.py` connected to `django.contrib.auth.get_user_model()`.

#### Why:
Ensures that the loyalty wallet infrastructure is inherently linked to user identity at the database level, eliminating the need for manual account creation during onboarding.

#### Prompt:

```
Register the RegisterView and ensure the Serializer handles user account creation.
```

#### What I accepted:
The usage of `generics.CreateAPIView` combined with a clean `UserSerializer` to handle the registration endpoint.

#### Why:
Leveraging built-in DRF generics ensured standard compliant REST behavior while allowing the pre-existing signal to trigger the account creation process automatically.

#### Prompt:

```
How do we structure our app labels and config to avoid the "Conflicting 'account' models" error?
```

#### What I accepted:
Explicitly setting `label = 'wallet'` and `label = 'accounts'` within the `AppConfig` classes and switching to absolute imports (`apps.wallet.models`).

#### Why:
Standardized the internal Django app registry, which was critical for resolving naming collisions between the Python package structure and Django's internal naming convention.

#### Prompt:

```
Add a unit test for the Accounts registration view.
```

#### What I accepted:
An `APITestCase` that posts to the registration endpoint and verifies the existence of both the `User` and the `Account` record.

#### Why:
This bridged the gap between our API layer and our model signal logic, confirming that the entire `Registration -> Account Provisioning` lifecycle works as expected in one request.
