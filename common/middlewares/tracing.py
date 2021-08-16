from contextlib import suppress
import falcon
from jaeger_client.tracer import Tracer

from opentracing import Format


class TracingMiddleware:
    def __init__(self, tracing_client: Tracer):
        self._tracing_client = tracing_client

    async def process_resource(self, req, resp, resource, params):
        # extract parent span (if any) from headers
        parent_span = None

        with suppress(Exception):
            parent_span = self._tracing_client.extract(format=Format.HTTP_HEADERS, carrier=req.headers)

        # create new span for request
        req.context.tracing_scope = self._tracing_client.start_active_span(
            operation_name=f'req-in:{req.path}:{req.method}',
            child_of=parent_span
        )

        req.context.tracing_client = self._tracing_client
    
    async def process_response(self, req, resp, resource, req_succeeded):
        # close request span
        if hasattr(req.context, 'tracing_scope'):
            if not req_succeeded:
                req.context.tracing_scope.span.log_event('request failed', {
                    'exception': f'{resp.status}:{resp.text}'
                })
            req.context.tracing_scope.close()
