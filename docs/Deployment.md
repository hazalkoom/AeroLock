# Azure VM Deployment Guide

This guide walks through deploying the AeroLock MVP onto your newly created Azure Virtual Machine (Standard_B2als_v2 in Sweden Central).

---

## 🔑 Step 1: Secure Your Private Key
Before you can connect, you must restrict the permissions on the private key file you downloaded (`aerolock_key.pem`). Run this on your local machine terminal:

```bash
chmod 400 "/run/media/hazalkoom/FD16124010E85459/big project/AreoLock/aerolock_key.pem"
```

## 🚀 Step 2: Log Into Your Azure VM
Run the following SSH command to connect to your remote virtual machine:

```bash
ssh -i "/run/media/hazalkoom/FD16124010E85459/big project/AreoLock/aerolock_key.pem" azureuser@<YOUR_AZURE_VM_PUBLIC_IP>
```
*(Replace `<YOUR_AZURE_VM_PUBLIC_IP>` with the public IP address listed on your Azure VM Dashboard).*

---

## 🛠️ Step 3: Install Docker and Docker Compose
Once you are logged into your Azure VM terminal, run these commands to install Docker:

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Docker dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common git nginx

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose V2
sudo apt install -y docker-compose-plugin

# Verify installations
docker --version
docker compose version
```

---

## 📦 Step 4: Clone and Configure the Project
Still logged inside the Azure VM, clone the repository and set up environment variables:

```bash
# Clone the repository
git clone https://github.com/hazalkoom/AeroLock.git
cd AeroLock

# Copy environment template
cp .env.example .env

# Edit environment variables (e.g. set your Postgres password)
nano .env
```

---

## ⚡ Step 5: Start the Microservices
Boot up the entire stack (Postgres, Redis, Gateway, Inventory, and Search) using Docker Compose:

```bash
sudo docker compose up -d --build
```

Verify that all five containers are healthy and running:
```bash
sudo docker compose ps
```

---

## 🗄️ Step 6: Seed mock flight data
Run the seeding script to populate PostgreSQL with mock flights and seat structures:

```bash
sudo docker compose exec inventory-service python db/seed.py
```

---

## 🌐 Step 7: Configure Nginx to routing traffic to the Gateway
To allow users to access the Gateway over the public IP without typing port `:8000`:

1. Open Nginx default configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```
2. Replace its content with the following:
   ```nginx
   server {
       listen 80;
       server_name localhost;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # Enable WebSockets
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```
3. Test and restart Nginx:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 📊 Monitoring the Deployment
To see how the containers are performing, run these commands inside the `AeroLock` directory:

| Task | Command |
| --- | --- |
| View Gateway Logs | `sudo docker compose logs -f gateway` |
| View Redis Memory | `sudo docker compose exec redis redis-cli INFO memory` |
| Active seat locks | `sudo docker compose exec redis redis-cli KEYS "seat:*:lock"` |
| Check Postgres status | `sudo docker compose exec postgres pg_isready -U aerolock_user -d aerolock` |