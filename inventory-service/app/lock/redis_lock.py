import uuid
from redis.asyncio import Redis

class RedisLockManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.lock_timeout = 720

    async def acquire_lock(self, seat_id: str) -> tuple[bool, str]:
        lock_key = f"seat:{seat_id}:lock"
        token = str(uuid.uuid4())

        success = await self.redis.set(lock_key, token, nx=True, ex=self.lock_timeout)
        
        if success:
            return True, token
        return False, ""

    async def release_lock(self, seat_id: str, token: str) -> bool:
        lock_key = f"seat:{seat_id}:lock"
        
        # Inline Lua script to ensure atomicity: only delete if the token matches!
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = await self.redis.eval(lua_script, 1, lock_key, token)
        return bool(result)