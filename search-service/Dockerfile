FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir grpcio grpcio-tools redis hiredis asyncpg sqlalchemy pydantic-settings

COPY shared/ /app/shared/
COPY search-service/ /app/search-service/

RUN pip install --no-cache-dir -e /app/shared

WORKDIR /app/search-service

EXPOSE 50051

CMD ["python", "-m", "app.main"]