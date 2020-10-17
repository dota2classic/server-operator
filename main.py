import datetime
import json
import asyncio as aio
import time

import aioredis
import aioschedule as schedule

from config import REDIS_PORT, REDIS_HOST
from gs.util import is_server_running
from process.match_created import process_match_created_event
from server import flask_app
from servers import supported_servers

# 10 secs
DOWN_CONFIRMED_THRESHOLD = 30


async def actualize_servers(redis_queue):
    for ip, p in supported_servers.items():
        is_running = is_server_running(ip)
        if not is_running and supported_servers[ip]['down_for'] < DOWN_CONFIRMED_THRESHOLD:
            if supported_servers[ip]['down_for'] == 0:
                supported_servers[ip]['down_for'] = 1
                supported_servers[ip]['down_since'] = time.time()
            else:
                supported_servers[ip]['down_for'] = time.time() - supported_servers[ip]['down_since']
                if supported_servers[ip]['down_for'] >= DOWN_CONFIRMED_THRESHOLD:
                    await redis_queue.publish_json('GameServerStoppedEvent', {
                        'url': ip,
                        'version': 'Dota_681'
                    })


async def handle_match_created(redis_queue):
    channel = (await redis_queue.subscribe('GameSessionCreatedEvent'))[0]

    while await channel.wait_message():
        message = json.loads(await channel.get(encoding='utf-8'))
        await process_match_created_event(redis_queue, message['data'])


async def init_redis_queue():
    redis_queue = await aioredis.create_redis_pool('redis://%s:%d' % (REDIS_HOST, REDIS_PORT) )

    return redis_queue


async def checks(redis_queue):
    schedule.every(3).seconds.do(actualize_servers, redis_queue)
    while True:
        await schedule.run_pending()
        await aio.sleep(1)



async def start_server():
    flask_app.run(host='0.0.0.0', port = 5001)

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
loop.create_task(start_server())
loop.run_forever()
