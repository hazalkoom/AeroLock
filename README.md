# AeroLock

AeroLock is a real-time, distributed backend API engine that prevents double-booking of flight seats using a Redis distributed lock and a PostgreSQL ACID ledger. It features extremely low-latency reads via Redis cache-aside and bullet-proof idempotent booking confirmations.

🚀 **Performance Benchmarks:** Our local development infrastructure sustains up to **800 concurrent users** and **over 300+ Requests Per Second (RPS)** with **0% failure rate** and a 95th percentile latency of under 350ms!

## ⚡ Quick Start

1. **Start the Stack** (Postgres, Redis, Gateway, Search, Inventory):
   ```bash
   ./scripts/run_local.sh
   ```

2. **Access the API**:
   - Swagger Documentation: `http://localhost:8000/docs`
   - Gateway Health: `http://localhost:8000/health`
   - Test endpoints: `/api/v1/search` and `/api/v1/booking/lock`

3. **Run the Tests**:
   - E2E Tests: `cd tests && poetry run pytest e2e/`
   - Security Suite: `cd tests && poetry run pytest security/`
   - Load Testing: `cd tests && poetry run locust -f performance/locustfile.py`

## 📚 Documentation

For full project details, architecture maps, and development logs, please explore the [docs/](docs/) folder:

- 🗺️ **[context.md](docs/context.md)**: Fast-start map for the repository layout and service architecture.
- 📊 **[report.md](docs/report.md)**: Current development status, completed milestones, and upcoming roadmap.
- 🏗️ **[Architecture.md](docs/Architecture.md)**: Detailed system architecture, data models, and component responsibilities.
- 🚀 **[Deployment.md](docs/Deployment.md)**: Instructions for deploying the MVP on a single VPS.
- 🆓 **[Deployment_Free.md](docs/Deployment_Free.md)**: Instructions for deploying using free-tier services (Render, Supabase, Upstash).
- 🧠 **[Design_Decisions.md](docs/Design_Decisions.md)**: Log of technical design choices and trade-offs.
- 📚 **[Learning_Path.md](docs/Learning_Path.md)**: A guided checklist for understanding the stack (FastAPI, Redis, Postgres, gRPC).
- 📋 **[Requirements.md](docs/Requirements.md)**: Core functional and non-functional requirements of the system.
- 🧪 **[Testing.md](docs/Testing.md)**: Strategy and instructions for Unit, E2E, Performance, and Security testing.
- 🌐 **[api.md](docs/api.md)**: Reference for the public REST endpoints and internal gRPC APIs.