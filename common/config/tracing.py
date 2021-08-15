from jaeger_client import Config
from opentracing import Format
from opentracing.scope_managers.asyncio import AsyncioScopeManager


def initialize_tracing_client(
    service_name,
    reporting_host='localhost',
    reporting_port='6831'
):
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'local_agent': {'reporting_host': reporting_host, 'reporting_port': reporting_port},
        },
        service_name=service_name,
        validate=True,
        scope_manager=AsyncioScopeManager()
    )

    return config.initialize_tracer()
