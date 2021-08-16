import falcon.asgi

from common.config.tracing import initialize_tracing_client
from common.middlewares.tracing import TracingMiddleware
from common.config.redis import initialize_redis

from delivery.resources import register_resources
from delivery.middlewares.redis import RedisMiddleware

class App:
    def __init__(self):
        self._is_setup = False
        self._app = None
    
    async def _setup(self):
        tracing_client = initialize_tracing_client('delivery_service')
        redis = await initialize_redis()
        self._app = falcon.asgi.App(middleware=[
            TracingMiddleware(tracing_client),
            RedisMiddleware(redis)
        ])
        register_resources(self._app)
        self._is_setup = True
        print('setup')
    
    async def __call__(self, scope, receive, send):
        if not self._is_setup:
            await self._setup()
        return await self._app(scope, receive, send)

app = App()
