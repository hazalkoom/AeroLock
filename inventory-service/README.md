# Inventory Service

A gRPC microservice responsible for handling flight seat locks and confirmation ledgers. It ensures seat-booking exclusivity using Redis distributed locking and PostgreSQL ACID transactions.

## Directory Structure

```text
inventory-service/
├── app/
│   ├── core/             # Configuration and logging utilities
│   ├── db/               # SQLAlchemy models and repositories
│   ├── lock/             # Redis SET NX distributed locking implementation
│   ├── services/         # gRPC endpoint servicer (AcquireLock, ConfirmBooking)
│   └── main.py           # gRPC server startup entrypoint
├── db/                   # Database schemas and database seeding scripts
├── tests/
│   └── unit/             # Mock-based unit tests for db repositories & locks
└── pyproject.toml        # Poetry configuration
```

## How to Run Independently

```bash
# 1. Install dependencies
poetry install

# 2. Set environment variables (requires running Postgres and Redis)
export DATABASE_URL="postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock"
export REDIS_URL="redis://localhost:6379/0"

# 3. Run the gRPC server
poetry run python -m app.main
```

## Running Unit Tests

To run the isolated unit tests (uses mock database sessions and mocked Redis clients):

```bash
poetry run pytest
```
