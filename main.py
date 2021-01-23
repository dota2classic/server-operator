import asyncio
import json
import asyncio as aio
import time

import aioredis
import aioschedule as schedule

from config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from gs.run_server import run_server
from gs.util import is_server_running
from process.kill_requested import process_kill_requested_event
from process.match_created import process_match_created_event
from config.servers import supported_servers, find_server

# 10 secs
from process.process_actualization_requested import process_actualization_requested

DOWN_CONFIRMED_THRESHOLD = 10


def wrap_reply(orig_message, reply):
    return {
        'response': reply,
        "isDisposed": True,
        "id": orig_message['id']
    }


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
        await redis_queue.publish_json('GameServerDiscoveredEvent', {
            'url': ip,
            'version': p['version']
        })


async def handle_kill_requested(redis_queue):
    channel = (await redis_queue.subscribe('KillServerRequestedEvent'))[0]

    async def reader(ch):
        async for msg in ch.iter():
            message = json.loads(msg)
            await process_kill_requested_event(redis_queue, message['data'])

    asyncio.ensure_future(reader(channel))


async def handle_match_created(redis_queue):
    pass
    # channel = (await redis_queue.subscribe('GameSessionCreatedEvent'))[0]
    #
    # async def reader(ch):
    #     async for msg in ch.iter():
    #         message = json.loads(msg)
    #         await process_match_created_event(redis_queue, message['data'])
    #
    # asyncio.get_running_loop().create_task(reader(channel))


async def handle_actualization_requested(redis_queue):
    channel = (await redis_queue.subscribe('ServerActualizationRequestedEvent'))[0]

    async def reader(ch):
        async for msg in ch.iter():
            message = json.loads(msg)
            await process_actualization_requested(redis_queue, message['data'])

    asyncio.ensure_future(reader(channel))


async def handle_discovery_requested(redis_queue):
    channel = (await redis_queue.subscribe('DiscoveryRequestedEvent'))[0]

    async def reader(ch):
        async for msg in ch.iter():
            await server_discovery(redis_queue)

    asyncio.ensure_future(reader(channel))



async def launch_server(message, pub):
    try:
        evt = message['data']
        print("Received launch command on ")
        print(evt)

        ip, server = find_server(evt['url'])

        is_running = is_server_running(ip)

        print("%d is running" % is_running)

        if is_running:
            await pub.publish_json('LaunchGameServerCommand.reply', wrap_reply(message, {
                'successful': False
            }))

        good = run_server(ip, server, evt['matchId'], evt['info'])

        print("%d is good" % good)
        if good:
            server['down_for'] = 0
            server.pop('down_since', None)

            await pub.publish_json('LaunchGameServerCommand.reply', wrap_reply(message, {
                'successful': True
            }))

            await pub.publish_json('GameServerStartedEvent', ({
                'matchId': evt['matchId'],
                'info': evt['info'],
                'url': ip
            }))


        else:
            await pub.publish_json('LaunchGameServerCommand.reply', wrap_reply(message, {
                'successful': False
            }))
    except ValueError:
        print("There is no such server here, skipping")

async def handle_launch_command(redis_queue_asd):
    pub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    sub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    channel = (await sub.subscribe('LaunchGameServerCommand'))[0]

    print("LaunchGameServerCommand subscribe")

    async def reader(ch):
        async for msg in ch.iter():
            print("I read it !! ")
            await launch_server(json.loads(msg), pub)


    loop = asyncio.get_event_loop()
    loop.create_task(reader(channel))


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
    asyncio.ensure_future(handle_launch_command(redis_queue))

    # asyncio.ensure_future(handle_actualization_requested(redis_queue))
    # asyncio.ensure_future(handle_kill_requested(redis_queue))
    # asyncio.ensure_future(checks(redis_queue))
    # asyncio.ensure_future(server_discovery(redis_queue))
    # asyncio.ensure_future(handle_discovery_requested(redis_queue))


asyncio.get_event_loop().create_task(start())
asyncio.get_event_loop().run_forever()

# is_server_running('glory.dota2classic.ru:27015')
