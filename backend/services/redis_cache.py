import os, redis

_redis = None
def get_redis():
    global _redis
    if _redis is None:
        _redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
    return _redis

def cache_get(key: str) -> str | None:
    return get_redis().get(key)

def cache_setex(key: str, ttl: int, value: str):
    get_redis().setex(key, ttl, value)