# AeroLock Search Service

This service provides lightning-fast search capabilities for flights and seats.

## What it does

The Search Service is optimized for read-heavy operations:
*   **Caching**: It uses Redis extensively to cache search results and availability data, reducing the load on the primary Postgres database.
*   **Querying**: It provides endpoints to find flights based on various criteria.
*   **gRPC Server**: It communicates with the Gateway via gRPC for high-speed data transfer.

## Structure
*   `grpc_server/`: Implementation of the search gRPC servicers.
*   `services/`: Core logic for caching and database lookups.
*   `Dockerfile`: Instructions for building the container image for this service.

## Running Locally

To run this service independently:
```bash
poetry install --no-root
poetry run python -m grpc_server.main
```
*(Note: Requires Postgres and Redis to be running)*
