import falcon.asgi

from common.config.tracing import initialize_tracing_client
from common.middlewares.tracing import TracingMiddleware

from order.resources import register_resources

tracing_client = initialize_tracing_client('service_a')
app = falcon.asgi.App(middleware=[TracingMiddleware(tracing_client)])

register_resources(app)
