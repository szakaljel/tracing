import json
from random import random

from uuid import uuid4
from opentracing.propagation import Format
import falcon


CHANNEL_NAME = 'channel:tasks'

class DeliveryResource:
    async def on_post(self, req, resp):

        data = await req.get_media()
        delivery = self._create_delivery(data)

        # random fail
        if random() < 0.3:
            order_id = delivery['order_id']
            raise Exception(f'error creating delivery for {order_id}')

        await self._send_delivery_event(
            delivery=delivery,
            redis=req.context.redis,
            tracing_client=req.context.tracing_client,
            tracing_span=req.context.tracing_scope.span
        )

        resp.status = falcon.HTTP_200 # pylint: disable=no-member
        resp.media = delivery

    async def _send_delivery_event(self, delivery, redis, tracing_client, tracing_span):
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

    @staticmethod
    def _create_delivery(data):
        return {
            'id': uuid4().hex,
            'address': data.get('address', ''),
            'order_id': data.get('order_id', '')
        }

def register_resources(app):
    delivery_resource = DeliveryResource()

    app.add_route('/api/deliveries', delivery_resource)
