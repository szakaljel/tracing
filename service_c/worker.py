import asyncio
from contextlib import suppress
from functools import wraps
import json
import aioredis
from opentracing.propagation import Format

from common.config.redis import initialize_redis
from common.config.tracing import initialize_tracing_client


CHANNEL_NAME = 'channel:tasks'

def trace(tracing_client):
    def _trace(func):
        @wraps(func)
        async def with_tracing(message):
            parent_span = None
            with suppress(Exception):
                parent_span = tracing_client.extract(format=Format.TEXT_MAP, carrier=message['context'])
            with tracing_client.start_active_span(
                operation_name=f'process:message',
                child_of=parent_span
            ):
                return await func(message)
        return with_tracing
    return _trace

async def reader(channel: aioredis.client.PubSub, handler):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True, timeout=10.0)
        if not message:
            print('no message')
            continue
        message = json.loads(message['data'])
        await handler(message)

async def main() -> None:
    redis = await initialize_redis()
    tracing_client = initialize_tracing_client('service_c')

    @trace(tracing_client)
    async def handle_message(message):
        await asyncio.sleep(0.5)
        print(message)

    psub = redis.pubsub()
    async with psub as p:
        await p.subscribe(CHANNEL_NAME)
        await reader(p, handle_message)
        await p.unsubscribe(CHANNEL_NAME)

    await psub.close()

if __name__ == '__main__':
    asyncio.run(main())