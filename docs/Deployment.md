# Deployment

## MVP Deployment Target

AeroLock's MVP is deployed via **Docker Compose on a single VPS**. This is a
deliberate choice (see `Design_Decisions.md`, D-008) — at 18.5 peak RPS, a
single VPS has enormous headroom, and Kubernetes would add operational
overhead with no functional benefit for this scale.

Kubernetes manifests exist under `k8s/` as the **ideal production
architecture** for the planning document, but are not used for the MVP.

---

## 1. Provision the VPS

- Provider: Hetzner Cloud
- Plan: CPX31 (4 vCPU, 8 GB RAM, 160 GB SSD) — see Infrastructure section
  of the planning PDF for sizing rationale
- OS: Ubuntu 22.04 LTS

```bash
ssh root@<vps-ip>
```

## 2. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker-compose nginx certbot python3-certbot-nginx git
```

## 3. Clone and Configure

```bash
git clone https://github.com/<you>/aerolock.git
cd aerolock
cp .env.example .env
# edit .env: set POSTGRES_PASSWORD, REDIS settings, API keys for rate limiting
```

## 4. Start the Stack

```bash
sudo docker-compose up -d
sudo docker-compose ps   # confirm all 5 containers are healthy
```

Services started: `gateway`, `search-service`, `inventory-service`, `redis`,
`postgres`.

## 5. Seed the Database

```bash
sudo docker-compose exec inventory-service python db/seed.py
```

This populates `flights` and `seats` with mock data for the demo.

## 6. Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/aerolock
server {
    listen 80;
    server_name api.aerolock.example.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/aerolock /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 7. Enable HTTPS

```bash
sudo certbot --nginx -d api.aerolock.example.com
```

## 8. Verify

```bash
curl https://api.aerolock.example.com/health
curl "https://api.aerolock.example.com/search?origin=CAI&destination=JFK"
```

---

## Open Ports

| Port   | Service           | Exposure                          |
| ------ | ------------------ | ------------------------------------ |
| 8000   | Gateway REST API   | Internal only (proxied by Nginx)   |
| 50051  | Search gRPC        | Internal Docker network only      |
| 50052  | Inventory gRPC     | Internal Docker network only      |
| 6379   | Redis              | Internal Docker network only      |
| 5432   | PostgreSQL         | Internal Docker network only      |
| 80/443 | Nginx              | Public                              |

---

## Updating a Running Deployment

```bash
cd aerolock
git pull
sudo docker-compose up -d --build
```

---

## Monitoring

| What to check     | Command                                                  |
| -------------------- | ----------------------------------------------------------- |
| Service logs       | `docker compose logs -f gateway`                        |
| Redis memory       | `docker compose exec redis redis-cli INFO memory`       |
| Active seat locks  | `docker compose exec redis redis-cli KEYS "seat:*:lock"` |
| Postgres activity  | `docker compose exec postgres psql -U aerolock -c "SELECT * FROM pg_stat_activity;"` |
| Container health   | `docker compose ps`                                      |

---

## Rollback

```bash
git log --oneline           # find previous commit hash
git checkout <previous-hash>
sudo docker-compose up -d --build
```