class RedisMiddleware:

    def __init__(self, redis_awaitable):
        self._redis = None
        self._redis_awaitable = redis_awaitable
    
    async def process_startup(self, scope, event):
        self._redis = await self._redis_awaitable

    async def process_resource(self, req, resp, resource, params):
        req.context.redis = self._redis
