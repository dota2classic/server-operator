import json
import asyncio as aio

import aioredis
import aioschedule as schedule

from gs.util import is_server_running
from process.match_created import process_match_created_event
from servers import supported_servers

DOWN_CONFIRMED_THRESHOLD = 2


async def actualize_servers(redis_queue):
    print('Actualizing server statuses')
    for ip, p in supported_servers.items():
        is_running = is_server_running(ip)
        if not is_running and supported_servers[ip]['down_for'] < DOWN_CONFIRMED_THRESHOLD:
            supported_servers[ip]['down_for'] += 1
            if supported_servers[ip]['down_for'] == DOWN_CONFIRMED_THRESHOLD:
                await redis_queue.publish_json('GameServerStoppedEvent', {
                    'url': ip,
                    'version': 'Dota_681'
                })
    print(json.dumps(supported_servers))


async def handle_match_created(redis_queue):
    channel = (await redis_queue.subscribe('GameSessionCreatedEvent'))[0]

    while await channel.wait_message():
        message = json.loads(await channel.get(encoding='utf-8'))
        await process_match_created_event(redis_queue, message['data'])


async def init_redis_queue():
    redis_queue = await aioredis.create_redis_pool('redis://localhost:6379')

    return redis_queue


async def checks(redis_queue):
    schedule.every(3).seconds.do(actualize_servers, redis_queue)
    while True:
        await schedule.run_pending()
        await aio.sleep(1)


# export class GameServerStoppedEvent {
#   constructor(
#     public readonly url: string,
#     public readonly version: Dota2Version,
#   ) {}
# }


async def start():
    redis_queue = await init_redis_queue()
    loop.create_task(handle_match_created(redis_queue))
    loop.create_task(checks(redis_queue))


loop = aio.get_event_loop()
loop.create_task(start())
loop.run_forever()
