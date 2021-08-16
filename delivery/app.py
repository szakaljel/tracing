from service_b.middlewares.redis import RedisMiddleware
import falcon.asgi

from common.config.tracing import initialize_tracing_client
from common.middlewares.tracing import TracingMiddleware
from common.config.redis import initialize_redis

from service_b.resources import register_resources

tracing_client = initialize_tracing_client('service_b')
redis_awaitable = initialize_redis()
app = falcon.asgi.App(middleware=[
    TracingMiddleware(tracing_client),
    RedisMiddleware(redis_awaitable)
])

register_resources(app)
