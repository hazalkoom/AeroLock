import json
import hashlib
from redis.asyncio import Redis
from app.core.config import settings
from app.core.logging import logger

class CacheManager:
    def __init__(self):
        # Decode responses ensures we get Python strings back, not raw bytes
        self.redis: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = settings.CACHE_TTL

    def _generate_key(self, origin: str, destination: str, departure_date: str) -> str:
        """
        Creates a deterministic, hashed Redis key based on the exact search parameters.
        """
        raw_string = f"{origin}-{destination}-{departure_date}".lower().strip()
        # We hash it so the Redis keys don't become massively long strings
        key_hash = hashlib.md5(raw_string.encode()).hexdigest()
        return f"search:flights:{key_hash}"

    async def get_cached_search(self, origin: str, destination: str, departure_date: str) -> list | None:
        key = self._generate_key(origin, destination, departure_date)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                logger.info(f"Cache HIT for key: {key}")
                return json.loads(cached_data)
                
            logger.info(f"Cache MISS for key: {key}")
            return None
        except Exception as e:
            # If Redis crashes, we DO NOT want the whole app to crash. 
            # We log the error and return None so it falls back to PostgreSQL.
            logger.error(f"Redis GET Error (Failing Open): {e}")
            return None

    async def set_cached_search(self, origin: str, destination: str, departure_date: str, flight_data: list):
        key = self._generate_key(origin, destination, departure_date)
        try:
            # We serialize the Python list to JSON and set the expiration timer (TTL)
            await self.redis.set(key, json.dumps(flight_data), ex=self.ttl)
            logger.info(f"Cached data SET for key: {key} (Expires in {self.ttl}s)")
        except Exception as e:
            logger.error(f"Redis SET Error: {e}")