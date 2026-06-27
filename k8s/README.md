# AeroLock Kubernetes Infrastructure

This directory contains the Kubernetes (K8s) manifests required to deploy the AeroLock system in a production-ready environment.

## What is Kubernetes?

Kubernetes (often abbreviated as **K8s**) is an open-source system for automating the deployment, scaling, and management of containerized applications (like Docker containers). 

Instead of manually starting containers on a server using `docker-compose up`, Kubernetes acts like a conductor. You give it these YAML files (which describe the *desired state* of your application), and Kubernetes automatically figures out how to make it happen across a cluster of servers (Nodes). If a container crashes, Kubernetes restarts it. If traffic spikes, Kubernetes can scale up the number of copies (replicas) of your service.

## Directory Structure

*   `config/`: Contains `configmap.yaml` (for environment variables) and `secrets.yaml` (for sensitive passwords, currently using base64 encoded dummy values).
*   `databases/`: Contains `postgres.yaml` and `redis.yaml`. These use `StatefulSet` resources because databases need persistent storage.
*   `services/`: Contains the deployments and services for our custom microservices: `gateway`, `inventory-service`, and `search-service`.
*   `ingress/`: Contains `ingress.yaml` which configures how external traffic from the internet reaches the `gateway`.

## How to Deploy

1. Ensure you have a running Kubernetes cluster and `kubectl` configured.
2. Build and push your Docker images to a registry (e.g., Docker Hub or GitHub Container Registry).
3. Apply the manifests in the following order:
   ```bash
   kubectl apply -f k8s/config/
   kubectl apply -f k8s/databases/
   # Wait for databases to be running
   kubectl apply -f k8s/services/
   kubectl apply -f k8s/ingress/
   ```
