# Search Service

A gRPC microservice responsible for querying and caching flight schedules. It features high performance reads using a Redis cache-aside caching pattern.

## Directory Structure

```text
search-service/
├── app/
│   ├── core/             # Configuration and logging utilities
│   ├── db/               # SQLAlchemy models and repositories
│   ├── server.py         # gRPC server implementation
│   ├── cache.py          # Redis Cache Manager
│   └── main.py           # Server entrypoint
├── tests/
│   └── unit/             # Unit tests for repositories and cache mechanisms
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

To run the isolated unit tests (which mock the database session and Redis storage):

```bash
poetry run pytest
```
