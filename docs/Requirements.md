# Requirements

## 1. The Vision
Build a real-time backend API that stops the double-booking race condition dead in its tracks. We use a high-speed **Redis lock** and a **PostgreSQL ledger** to guarantee two people never buy the same seat, while keeping flight searches blazing fast.

## 2. Core User Flow (How It Works)
* **Step 1: Search.** Clients ask for flights. We serve this instantly from a **Redis cache** (optimized for speed/availability).
* **Step 2: Hold Seat.** User clicks "Book". We instantly grab a distributed lock in Redis (`SET NX`) with a **10-minute timeout (TTL)**.
    * *If lock fails:* Seat is taken. Respond immediately with `423 Locked`.
* **Step 3: Pay.** User goes to the simulated payment gateway.
* **Step 4: Webhook & Recovery (The Edge Case).** The payment webhook comes back confirming the transaction.
    * *If lock is still valid:* Great, proceed.
    * *If lock expired:* Do NOT panic-reject. Do a quick PostgreSQL DB check. If the seat is magically still empty, take the money and book it. If someone else took it, *then* we reject.
* **Step 5: Commit.** Save the final booking to **PostgreSQL**. You MUST use an **idempotency key** so if the webhook fires twice, we don't accidentally book or charge them twice.

## 3. Non-Functional Requirements
* **Speed (Latency Targets):**
    * Search p95: **< 80 ms**
    * Lock Acquisition p95: **< 50 ms**
* **Traffic (Throughput Limits):**
    * Peak Search: **18.5 RPS**
    * Peak Booking: **0.37 RPS**
    * *Hardware:* Because of these numbers, a single cloud VPS is enough.
* **Abuse Protection:**
    * Fixed rate limit of **100 requests/minute per API key** at the Gateway.
* **Rules of the Game:**
    * **Zero overselling:** Mutual exclusion on seats is absolute.
    * **Idempotency is mandatory:** All write operations must be safe to retry over the network.
* **What We Are NOT Doing (Out of Scope):**
    * No frontend / UI screens.
    * No real Amadeus/GDS API integration.
    * No real payment processors (no PCI-DSS compliance).
    * No complex multi-region cloud deployments.
    * No authentication / user accounts in v1.

## 4. Resolved Questions

* **Simulating payment gateway latency in E2E tests:** the mock payment
  endpoint accepts a configurable delay (`asyncio.sleep`) set via an
  environment variable, so tests can simulate both fast confirmations and
  slow webhooks that outlast the lock TTL.
* **Dangling locks if Redis crashes before AOF write:** not a separate
  concern. Redis AOF persists `SET ... PX` commands, and Redis recalculates
  the remaining TTL on restart. No background cleanup worker is required for
  the MVP.

## 5. Open Questions

* Should the 100 req/min rate limit be per API key or per IP for unauthenticated
  test traffic during the demo?
* What's the minimum set of seeded flights/seats needed to make the
  concurrent-booking demo convincing without being unrealistic?