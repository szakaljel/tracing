import asyncio
from contextlib import suppress
from functools import wraps
import json
from random import random

from jaeger_client.span import Span
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
            # extract parent span (if any) from event meta
            parent_span = None
            with suppress(Exception):
                meta = event.get('meta', {})
                parent_span = self._tracing_client.extract(format=Format.TEXT_MAP, carrier=meta)

            # create span for message processing
            with self._tracing_client.start_active_span(
                operation_name='process:delivery_event',
                child_of=parent_span
            ) as tracing_scope:
                try:
                    return await self._handler(event, self._tracing_client, tracing_scope)
                except Exception as ex: # pylint: disable=broad-except
                    tracing_scope.span.log_event('processing_error', {'message': str(ex)})
        return with_tracing


class EventHandler:

    async def __call__(self, event, tracing_client, tracing_scope):
        span: Span = tracing_scope.span
        order_id = event['data']['data']['order_id']
        span.log_event('start_processing', {'order_id': order_id})
        await self._process(event)
        span.log_event('end_processing', {'order_id': order_id})

    async def _process(self, event):
        print(event)

        # random fail
        if random() < 0.3:
            order_id = event['data']['data']['order_id']
            raise Exception(f'error during processin delivery of order {order_id}')

        await asyncio.sleep(0.2)


async def main() -> None:
    redis = await initialize_redis()
    tracing_client = initialize_tracing_client('notification_service')

    handler = EventHandler()
    worker = Worker(handler, redis, tracing_client)
    await worker.start()

if __name__ == '__main__':
    asyncio.run(main())
