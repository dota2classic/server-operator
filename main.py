import asyncio
import json
import asyncio as aio
import time

import aioredis
import aioschedule as schedule

from config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from gs.util import is_server_running
from process.kill_requested import process_kill_requested_event
from process.match_created import process_match_created_event
from config.servers import supported_servers

# 10 secs
DOWN_CONFIRMED_THRESHOLD = 10


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


async def server_discovery(redis_queue):
    for ip, p in supported_servers.items():
        print(json.dumps({
            'url': ip,
            'version': p['version']
        }))
        await redis_queue.publish_json('GameServerDiscoveredEvent', {
            'url': ip,
            'version': p['version']
        })
        print("Released discovered event")



async def handle_kill_requested(redis_queue):
    channel = (await redis_queue.subscribe('KillServerRequestedEvent'))[0]
    async def reader(ch):
        async for msg in ch.iter():
            message = json.loads(msg)
            await process_kill_requested_event(redis_queue, message['data'])

    asyncio.get_running_loop().create_task(reader(channel))


async def handle_match_created(redis_queue):
    channel = (await redis_queue.subscribe('GameSessionCreatedEvent'))[0]

    async def reader(ch):
        async for msg in ch.iter():
            message = json.loads(msg)
            await process_match_created_event(redis_queue, message['data'])

    asyncio.get_running_loop().create_task(reader(channel))




async def handle_discovery_requested(redis_queue):
    channel = (await redis_queue.subscribe('DiscoveryRequestedEvent'))[0]


    async def reader(ch):
        async for msg in ch.iter():
            await server_discovery(redis_queue)

    asyncio.get_running_loop().create_task(reader(channel))




async def checks(redis_queue):
    schedule.every(3).seconds.do(actualize_servers, redis_queue)
    while True:
        await schedule.run_pending()
        await aio.sleep(2)



# export class GameServerStoppedEvent {
#   constructor(
#     public readonly url: string,
#     public readonly version: Dota2Version,
#   ) {}
# }


async def start():
    redis_queue = await aioredis.create_redis_pool('redis://%s:%d' % (REDIS_HOST, REDIS_PORT), password=REDIS_PASSWORD)
    loop.create_task(handle_match_created(redis_queue))
    loop.create_task(handle_kill_requested(redis_queue))
    loop.create_task(checks(redis_queue))
    loop.create_task(server_discovery(redis_queue))
    loop.create_task(handle_discovery_requested(redis_queue))


loop = aio.get_event_loop()
loop.create_task(start())
loop.run_forever()

# is_server_running('glory.dota2classic.ru:27015')