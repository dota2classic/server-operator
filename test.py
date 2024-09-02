import asyncio
import json
import asyncio as aio

from redis import asyncio as aioredis

from config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


def wrap_reply(orig_message, reply):
    return {
        'response': reply,
        "isDisposed": True,
        "id": orig_message['id']
    }


async def test(redis_queue):
    channel = (await redis_queue.subscribe('SimpleQuery'))[0]

    # channel2 = (await redis_queue.subscribe('SimpleQuery.reply'))[0]

    async def reader(ch):
        async for msg in ch.iter():
            message = json.loads(msg)
            print(message)

            await redis_queue.publish_json('SimpleQuery.reply', wrap_reply(message, {
                'url': message['data']['url'],
                'pong': message['data']['ping'],

            }))

    asyncio.get_running_loop().create_task(reader(channel))


async def start():
    redis_queue = await aioredis.create_redis_pool('redis://%s:%d' % ('localhost', 6379))
    loop.create_task(test(redis_queue))

    print("pepega")


loop = aio.get_event_loop()
loop.create_task(start())
loop.run_forever()
