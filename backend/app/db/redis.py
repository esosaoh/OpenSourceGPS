import redis.asyncio as redis

async def init_redis_pool(host="redis", port=6379, db=0):
    """Initialize Redis connection pool"""
    redis_pool = redis.Redis(
        host=host,
        port=port,
        db=db,
        decode_responses=True
    )
    return redis_pool
