# Free Deployment (No Credit Card Required)

This is an alternative to `Deployment.md` for anyone without a credit card.
It swaps the single-VPS approach for three free managed platforms, all of
which work **without payment details**, verified as of June 2026.

## The Stack

| Component                | Platform   | Free Tier Limit                          | Card Required |
| --------------------------- | ----------- | ------------------------------------------- | ---------------- |
| Gateway, Search, Inventory  | **Render**  | 750 instance-hours/month total, sleeps after 15 min idle<sup>[1]</sup> | No |
| PostgreSQL                  | **Supabase**| 500 MB DB, 2 free projects, 5 GB bandwidth<sup>[1]</sup> | No |
| Redis                       | **Upstash** | 10,000 commands/day<sup>[2]</sup>          | No |

This setup is genuinely free forever for a demo-scale project — but it
comes with real trade-offs you should document honestly in
`Design_Decisions.md` as **free-tier MVP compromises**.

---

## 1. Why this requires small architecture changes

On a single VPS, your 3 services talk over Docker's internal network and
nobody else can reach Redis/Postgres directly. Across 3 separate free
platforms, every connection happens over the **public internet with TLS**:

- gRPC calls between Gateway ↔ Search ↔ Inventory use **gRPC over TLS**
  (grpc.secure_channel) instead of plaintext internal gRPC
- Redis and Postgres connection strings point to Upstash/Supabase's public
  endpoints (both provide TLS connection strings by default)

This is more realistic anyway — many real systems run this way.

---

## 2. Set up Supabase (PostgreSQL)

1. Sign up at supabase.com with email/GitHub — **no card**
2. Create a project (free tier: 500 MB)
3. Go to Project Settings → Database → copy the **connection string**
   (use the "Session pooler" connection for serverless-friendly behavior)
4. Run your `schema.sql` against it:
   ```bash
   psql "<supabase-connection-string>" -f inventory-service/db/schema.sql
   python inventory-service/db/seed.py  # update DB_URL env var first
   ```

---

## 3. Set up Upstash (Redis)

1. Sign up at upstash.com with email/GitHub — **no card**
2. Create a Redis database (choose a region close to your Render region)
3. Copy the `rediss://` connection string (note: `rediss` = TLS-enabled)
4. Use this as `REDIS_URL` in all services that need Redis

### Important: 10,000 commands/day budget

Your Inventory Service's `SET NX` lock calls and Search Service's cache
reads/writes all count against this. At a *real* 18.5 RPS this would be
exhausted in minutes — but for a **course demo with manual/scripted
testing**, 10k/day is generous. To stay safely under budget:

- Increase search cache TTL from 60s → 5 minutes (fewer cache writes)
- Run your concurrent-booking demo test a handful of times, not in a loop

Document this explicitly in `Design_Decisions.md`:

> **D-011: Redis Command Budget (Free Tier)** — Upstash free tier caps
> Redis at 10,000 commands/day. The architecture and code are written for
> unlimited Redis (per the planning doc's RPS targets); the free-tier
> deployment simply operates at a smaller scale for demonstration purposes.

---

## 4. Deploy each service to Render

Render free tier: **one Web Service per repo/Dockerfile**, so each of your
3 services gets its own Render Web Service, all from the same GitHub repo
using different root directories.

1. Sign up at render.com with GitHub — **no card**
2. New → Web Service → connect your `aerolock` repo
3. For each service, set:
   - **Root Directory**: `gateway` / `search-service` / `inventory-service`
   - **Runtime**: Docker (Render detects your `Dockerfile`)
   - **Environment Variables**: `REDIS_URL` (Upstash), `DATABASE_URL`
     (Supabase), and the **public URLs of the other two Render services**
     for gRPC calls
4. Repeat for all 3 services — you'll get 3 URLs like:
   ```
   https://aerolock-gateway.onrender.com
   https://aerolock-search.onrender.com
   https://aerolock-inventory.onrender.com
   ```

### gRPC over Render

Render's free web services terminate TLS for you and expose port 443.
Configure your gRPC clients to connect via `grpc.secure_channel()` to
`<service>.onrender.com:443` using the default SSL credentials.

---

## 5. Cold Starts — what to expect

Free Render services **sleep after 15 minutes of no traffic** and take
~30–60 seconds to wake on the next request<sup>[1]</sup>.

**Before recording your demo video:**

```bash
curl https://aerolock-gateway.onrender.com/health
curl https://aerolock-search.onrender.com/health
curl https://aerolock-inventory.onrender.com/health
# wait ~1 min for all three to wake up, then start recording
```

Mention this in your README so reviewers aren't confused by a slow first
request.

---

## 6. Updated `.env.example` for free deployment

```bash
# Supabase
DATABASE_URL=postgresql://postgres:[password]@[project].supabase.co:5432/postgres

# Upstash
REDIS_URL=rediss://default:[password]@[endpoint].upstash.io:6379

# Inter-service URLs (Render public endpoints, used for gRPC over TLS)
SEARCH_SERVICE_URL=aerolock-search.onrender.com:443
INVENTORY_SERVICE_URL=aerolock-inventory.onrender.com:443
```

---

## 7. What to tell reviewers

Add a short note to your root `README.md`:

> **Note on deployment:** The MVP is deployed across Render (compute),
> Supabase (PostgreSQL), and Upstash (Redis) free tiers — chosen because
> they require no payment method. The Docker Compose setup in this repo
> reflects the architecture for a single-VPS deployment as described in
> the planning document; the free-tier deployment uses the same containers
> against managed external Redis/Postgres instead of local containers for
> those two.

This is an honest, accurate statement — it shows you understand the
difference between your *designed* architecture and your *deployed*
instance, which is exactly the kind of distinction reviewers want to see.

---

## Sources

[1] Render, *Platforms with a real free tier for developers in 2026*, Apr 2026.
    https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026

[2] Koyeb, *Which Cloud Database Platform to Choose for Your Applications*.
    https://www.koyeb.com/blog/which-cloud-database-platform-to-choose-for-your-applications
