from contextlib import suppress
from jaeger_client.tracer import Tracer

from opentracing import Format


class TracingMiddleware:
    def __init__(self, tracing_client: Tracer):
        self._tracing_client = tracing_client

    async def process_resource(self, req, resp, resource, params):
        parent_span = None

        with suppress(Exception):
            parent_span = self._tracing_client.extract(format=Format.HTTP_HEADERS, carrier=req.headers)

        req.context.tracing_scope = self._tracing_client.start_active_span(
            operation_name=f'req-in:{req.path}:{req.method}',
            child_of=parent_span
        )

        req.context.tracing_client = self._tracing_client
    
    async def process_response(self, req, resp, resource, req_succeeded):
        if hasattr(req.context, 'tracing_scope'):
            if not req_succeeded:
                req.context.tracing_scope.span.log_event('request failed', {
                    'exception': 'unknown'
                })
            req.context.tracing_scope.close()
