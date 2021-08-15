import aiohttp
from aiohttp.typedefs import StrOrURL
from jaeger_client.tracer import Tracer
from opentracing.propagation import Format
from opentracing.span import Span


class TracingHttpClient(aiohttp.ClientSession):
    def __init__(self, tracing_client: Tracer, parent_span: Span):
        super().__init__()
        self._parent_span = parent_span
        self._tracing_client = tracing_client
    
    async def _request(
        self,
        method,
        str_or_url,
        **kwargs
    ):
        with self._tracing_client.start_active_span(
                operation_name=f'req-out:{str_or_url}:{method}',
                child_of=self._parent_span
            ) as scope:
            try:
                headers = kwargs.get('headers') or {}
                self._tracing_client.inject(scope.span.context, Format.HTTP_HEADERS, headers)
                kwargs['headers'] = headers

                return await super()._request(
                    method,
                    str_or_url,
                    **kwargs)
            except Exception as ex:
                scope.span.log_event('request failed', {
                    'exception': str(ex)
                })
                raise ex
