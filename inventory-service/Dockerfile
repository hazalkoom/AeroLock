FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir grpcio grpcio-tools redis hiredis asyncpg sqlalchemy alembic pydantic-settings

COPY shared/ /app/shared/
COPY inventory-service/ /app/inventory-service/

RUN pip install --no-cache-dir -e /app/shared

WORKDIR /app/inventory-service

EXPOSE 50052

CMD ["python", "-m", "app.main"]