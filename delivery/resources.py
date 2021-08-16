from opentracing.propagation import Format
import aioredis
import json
import falcon


CHANNEL_NAME = 'channel:tasks'

class DummyResource:
    async def on_get(self, req, resp):
        redis: aioredis.Redis = req.context.redis

        context = {}
        span_context = req.context.tracing_scope.span.context
        req.context.tracing_client.inject(span_context, Format.TEXT_MAP, context)

        await redis.publish(CHANNEL_NAME, json.dumps({
            'message': 'ciastko',
            'context': context
        }))

        resp.status = falcon.HTTP_200  # This is the default status
        resp.media = {
            'message': 'working'
        }

def register_resources(app):
    dummy_resource = DummyResource()

    app.add_route('/', dummy_resource)
