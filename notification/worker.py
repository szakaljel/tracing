import asyncio
from contextlib import suppress
from functools import wraps
import json

from opentracing.propagation import Format

from common.config.redis import initialize_redis
from common.config.tracing import initialize_tracing_client

class Worker:
    CHANNEL_NAME = 'channel:tasks'

    def __init__(self, handler, redis, tracing_client):
        self._redis = redis
        self._handler = handler
        self._tracing_client = tracing_client

    async def start(self):
        handler = self._prepare_handler()
        psub_manager = self._redis.pubsub()
        async with psub_manager as psub:
            await psub.subscribe(self.CHANNEL_NAME)
            while True:
                message = await psub.get_message(ignore_subscribe_messages=True, timeout=10.0)
                if not message:
                    print('no message')
                    continue
                message = json.loads(message['data'])
                await handler(message)
    
    def _prepare_handler(self):
        @wraps(self._handler)
        async def with_tracing(event):

            parent_span = None
            with suppress(Exception):
                parent_span = self._tracing_client.extract(format=Format.TEXT_MAP, carrier=event['meta'])
            
            with self._tracing_client.start_active_span(
                operation_name=f'process:delivery_event',
                child_of=parent_span
            ) as tracing_scope:
                return await self._handler(event, self._tracing_client, tracing_scope)
        return with_tracing


class EventHandler:

    async def __call__(self, event, tracing_client, tracing_scope):
        print(event)


async def main() -> None:
    redis = await initialize_redis()
    tracing_client = initialize_tracing_client('notification_service')

    handler = EventHandler()
    worker = Worker(handler, redis, tracing_client)
    await worker.start()

if __name__ == '__main__':
    asyncio.run(main())
