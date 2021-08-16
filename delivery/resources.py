import json

import falcon
from uuid import uuid4
from opentracing.propagation import Format


CHANNEL_NAME = 'channel:tasks'

class DeliveryResource:
    async def on_post(self, req, resp):

        data = await req.get_media()
        delivery = self.create_delivery(data)

        await self.send_delivery_event(
            delivery=delivery,
            redis=req.context.redis,
            tracing_client=req.context.tracing_client,
            tracing_span=req.context.tracing_scope.span
        )

        resp.status = falcon.HTTP_200
        resp.media = delivery

    async def send_delivery_event(self, delivery, redis, tracing_client, tracing_span):
        meta = {}
        span_context = tracing_span.context
        tracing_client.inject(span_context, Format.TEXT_MAP, meta)

        await redis.publish(CHANNEL_NAME, json.dumps({
            'data': {
                'event_type': 'delivery_created',
                'data': delivery
            },
            'meta': meta
        }))

    def create_delivery(self, data):
        return {
            'id': uuid4().hex,
            'address': data.get('address', ''),
            'order_id': data.get('order_id', '')
        }

def register_resources(app):
    delivery_resource = DeliveryResource()

    app.add_route('/api/deliveries', delivery_resource)
