# AeroLock Gateway Service

This is the API Gateway for the AeroLock platform. It serves as the primary entry point for all external client requests.

## What it does

The Gateway service acts as a reverse proxy and aggregator. Instead of external clients talking directly to the internal microservices (like Inventory or Search), they talk to the Gateway. The Gateway handles:
*   **Routing**: Directing REST API calls to the appropriate gRPC backend services.
*   **Rate Limiting**: Preventing abuse by limiting the number of requests a user can make.
*   **Real-Time WebSockets**: Managing WebSocket connections to push live seat availability updates to users using Redis Pub/Sub.

## Structure
*   `app/api/`: Contains the FastAPI routers and endpoints (including the `websocket.py` implementation).
*   `app/core/`: Core configurations, rate limiting, and dependency injection.
*   `Dockerfile`: Instructions for building the container image for this service.

## Running Locally

To run this service independently:
```bash
poetry install --no-root
poetry run uvicorn app.main:app --reload --port 8000
```
*(Note: Requires Postgres and Redis to be running)*
