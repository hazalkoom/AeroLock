#!/bin/bash

# Script to run OWASP ZAP baseline scan against the local API Gateway
# Requires Docker to be installed and running.

API_URL="http://host.docker.internal:8000"
CONF_FILE="zap-baseline.conf"

echo "Starting ZAP Baseline Scan against ${API_URL}..."

docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
    -t $API_URL \
    -c $CONF_FILE \
    -r zap-report.html

echo "Scan complete. Check tests/security/zap-report.html for results."
