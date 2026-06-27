# Gateway Service

FastAPI edge gateway acting as the REST translation layer to backend gRPC services. Enforces rate limiting (using SlowAPI), structured logging, and streams real-time updates via WebSockets.

## Directory Structure

```text
gateway/
├── app/
│   ├── api/             # REST & WebSocket Route Controllers
│   │   ├── booking.py   # Lock & Confirm REST API
│   │   ├── search.py    # Search API
│   │   └── websocket.py # Real-time flight update WebSocket
│   ├── clients/         # gRPC client wrappers to communicate with backend services
│   ├── core/            # Config, structured logging, and Event Pub/Sub helper
│   ├── middleware/      # Rate-limiting middleware (SlowAPI)
│   ├── schemas/         # Pydantic validation schemas
│   └── main.py          # FastAPI application entrypoint
├── tests/
│   └── unit/            # Gateway unit tests (mocked gRPC channels)
└── pyproject.toml       # Poetry configuration
```

## How to Run Independently

Make sure you have `poetry` installed:

```bash
# 1. Install dependencies
poetry install

# 2. Run the Gateway application locally (requires backend services to be running to forward requests)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Unit Tests

To run the unit tests independently (which use mock gRPC channels, no backend services required):

```bash
poetry run pytest
```
