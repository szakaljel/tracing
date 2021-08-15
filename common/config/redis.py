import aioredis

async def initialize_redis(
    redis_host='localhost',
    redis_port='6379'
):
    return await aioredis.from_url(f'redis://{redis_host}:{redis_port}')
