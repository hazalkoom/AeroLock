# AeroLock Inventory Service

This is the core Inventory Management service for the AeroLock platform.

## What it does

The Inventory Service is responsible for the central business logic of the application:
*   **Seat Locking**: Handling concurrent requests to lock seats for booking.
*   **Database Management**: Directly interacting with the PostgreSQL database using SQLAlchemy and Asyncpg.
*   **gRPC Server**: Providing a high-performance gRPC interface for the Gateway to communicate with.

## Structure
*   `db/`: Database models, migrations (Alembic), and seeding scripts.
*   `grpc_server/`: Implementation of the gRPC servicers defined in the shared protobufs.
*   `services/`: Core business logic for managing inventory.
*   `Dockerfile`: Instructions for building the container image for this service.

## Running Locally

To run this service independently:
```bash
poetry install --no-root
poetry run python -m grpc_server.main
```
*(Note: Requires Postgres and Redis to be running)*
