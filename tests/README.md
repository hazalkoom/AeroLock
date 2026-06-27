# AeroLock Testing Guide

Welcome to the testing suite for AeroLock! This repository contains automated checks for **End-to-End (E2E) flows**, **Performance/Load testing**, and **Security**.

## 1. Security Testing

Security tests run via `pytest` and validate that our API Gateway properly sanitizes inputs and correctly enforces IP-based rate limits.

**How to run:**
```bash
cd tests
poetry install
poetry run pytest security/
```

*Note: You may see simulated IPs testing the limits. The system enforces 20 req/min for Search and 10 req/min for Locking.*

## 2. End-to-End (E2E) Testing

The E2E suite runs against the full docker-compose stack. It dynamically finds an available seat in the database and fully simulates a concurrent race-condition to guarantee our Redis locking and PostgreSQL schemas prevent double bookings.

**How to run:**
Ensure `docker-compose up -d` is running at the project root, then:
```bash
cd tests
poetry run pytest e2e/
```

## 3. Performance Testing (Locust & k6)

We have two load-testing tools available to benchmark the infrastructure. 

### A. Locust (User Journey Simulation)
Locust simulates full user workflows (Searching -> Locking -> Confirming) in Python. 

**How to run:**
```bash
cd tests
poetry run locust -f performance/locustfile.py
```
Then open `http://localhost:8089` in your browser. 
*Recommended Settings for Local Machine: 200 to 800 Users, 20 Spawn Rate, host `http://localhost:8000`.*

### B. k6 (High-Concurrency Benchmarking)
k6 is used to bombard specific endpoints to test latency thresholds. 
*Note: Because our API has strict rate-limiting, tests like `k6_search.js` will intentionally trigger a 50% failure rate (`429 Too Many Requests`) if run for longer than 20 seconds, proving the security limiters work!*

**How to run (via Docker):**
```bash
# Test the Booking Write constraints
docker run --rm -i --network host grafana/k6 run - < tests/performance/k6_booking.js

# Test the Search Read constraints
docker run --rm -i --network host grafana/k6 run - < tests/performance/k6_search.js
```

> **Note on k6 Search failures:** The search k6 test will show ~50% failure rate. This is intentional and expected — it proves the rate limiter is working correctly by blocking requests after the per-IP limit is hit.

## 4. Real-Time WebSocket Manual Test

The gateway exposes a WebSocket endpoint for real-time seat status events. To test it manually:

```bash
# Install wscat (one-time)
npm install -g wscat

# Terminal 1: Connect to a flight's real-time feed
# Replace FLIGHT_ID with a real flight UUID from the database
wscat -c ws://localhost:8000/api/v1/ws/flights/FLIGHT_ID

# Terminal 2: Lock a seat on that flight
curl -X POST http://localhost:8000/api/v1/booking/lock \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 10.0.0.1" \
  -d '{"flight_id": "FLIGHT_ID", "seat_id": "SEAT_ID"}'

# Terminal 1 should instantly receive:
# {"flight_id": "...", "seat_id": "...", "status": "locked", "timestamp": "..."}
```
