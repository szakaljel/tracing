from uuid import uuid4
import falcon

from common.helpers.http_client import TracingHttpClient


class OrderResource:

    DELIVERY_SERVICE_URL = 'http://localhost:8002'

    async def on_post(self, req, resp):
        data = await req.get_media()
        order = self._create_order(data)

        delivery = await self._create_delivery(
            order_id = order['id'],
            address=data.get('address') or '',
            tracing_client = req.context.tracing_client,
            tracing_span = req.context.tracing_scope.span
        )

        resp.status = falcon.HTTP_200  # pylint: disable=no-member
        resp.media = {
            'order': order,
            'delivery': delivery
        }

    async def _create_delivery(self, order_id, address, tracing_client, tracing_span):
        async with TracingHttpClient(tracing_client, tracing_span) as client:
            async with client.post(
                f'{self.DELIVERY_SERVICE_URL}/api/deliveries',
                data = {
                    'order_id': order_id,
                    'address': address
                }
            ) as response:
                return await response.json()

    @staticmethod
    def _create_order(data):
        return {
            'id': uuid4().hex,
            'products': data.get('products', []),
            'status': 'delivery_in_progress'
        }


def register_resources(app):
    order_resource = OrderResource()

    app.add_route('/api/orders', order_resource)
