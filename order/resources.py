import falcon

from common.helpers.http_client import TracingHttpClient


class DummyResource:
    SERVICE_B_URL = 'http://localhost:8002'
    async def on_get(self, req, resp):
        
        service_b_response = await self.call_service_b(req)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.media = {
            'message': 'working',
            'service_b': service_b_response
        }
    
    async def call_service_b(self, req):
        async with TracingHttpClient(
            req.context.tracing_client,
            req.context.tracing_scope.span
        ) as session:
            async with session.get(self.SERVICE_B_URL) as response:
                return await response.json()

def register_resources(app):
    dummy_resource = DummyResource()

    app.add_route('/', dummy_resource)
