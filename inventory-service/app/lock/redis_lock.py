import uuid
from redis.asyncio import Redis

class RedisLockManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.release_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

    async def aquire_lock(self, flight_id: str, seat_id: str) -> tuple[bool, str | None]:
        lock_key = f"seat:{seat_id}:lock"
        token = str(uuid.uuid4())

        acquired = await self.redis.set(lock_key, token, nx=True, px=720000)

        if acquired:
            return True, token
        return False, None

    async def release_lock(self, flight_id: str, seat_id: str, token: str) -> bool:
        lock_key = f"seat:{seat_id}:lock"
        result = await self.redis.eval(self.release_script, 1, lock_key, token)
        return bool(result)