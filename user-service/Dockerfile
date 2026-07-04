FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY user-service/pyproject.toml ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

FROM python:3.12-slim

WORKDIR /app

# Copy installed python packages from builder (UPDATED TO 3.12)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the shared package and the service code
COPY shared /app/shared
COPY user-service /app/user-service

# Install the shared package in editable/pip mode to keep it container-friendly
RUN pip install -e /app/shared

EXPOSE 50053

ENV PYTHONPATH=/app/user-service

CMD ["python", "user-service/app/server.py"]