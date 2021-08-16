class RedisMiddleware:

    def __init__(self, redis):
        self._redis = redis

    async def process_resource(self, req, resp, resource, params):
        req.context.redis = self._redis
