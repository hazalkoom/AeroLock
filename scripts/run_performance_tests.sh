#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT_DIR"

echo "Performance harnesses are defined under tests/performance/."
echo "Run k6 or Locust against the live stack after starting docker compose."
