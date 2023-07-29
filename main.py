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
from config.servers import supported_servers, find_server

# 10 secs
from process.process_actualization_requested import process_actualization_requested

DOWN_CONFIRMED_THRESHOLD = 10

loop = asyncio.get_event_loop()


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
        await asyncio.sleep(1) # space for handling fast events


async def server_discovery():
    pub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    await server_discovery_inner(pub)


async def server_discovery_inner(pub):
    for ip, p in supported_servers.items():
        await pub.publish_json('GameServerDiscoveredEvent', {
            'url': ip,
            'version': p['version']
        })


async def launch_server(message, pub):
#     try:
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
#     except Exception as e:
#         print(e)
#         print("Error in launch_server, There is no such server here, skipping")


async def checks():
    pub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    while True:
        await actualize_servers(pub)
        await aio.sleep(5)


async def discovery_reader(pub, ch):
    print('Reading discovery')
    async for msg in ch.iter():
        print('Discovery...')
        await server_discovery_inner(pub)


async def launch_reader(pub, ch):
    print('Reading launch')
    async for msg in ch.iter():
        print('Launch...')
        await launch_server(json.loads(msg), pub)


async def actualization_reader(ch):
    print('Reading actualization')
    async for msg in ch.iter():
        # print('Actualization...')
        message = json.loads(msg)
        await aio.sleep(2)  # make space
        await process_actualization_requested(message['data'])


async def kill_reader(pub, ch):
    async for msg in ch.iter():
        print('Kill...')
        message = json.loads(msg)
        await process_kill_requested_event(pub, message['data'])


async def handle_events():
    pub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    sub = await aioredis.create_redis(
        'redis://%s:%d' % (REDIS_HOST, REDIS_PORT),
        password=REDIS_PASSWORD
    )
    [launch_channel, actual_channel, disc_channel, kill_channel] = (
        await sub.subscribe('LaunchGameServerCommand', 'ServerActualizationRequestedEvent', 'DiscoveryRequestedEvent',
                            'KillServerRequestedEvent'))

    loop.create_task(launch_reader(pub, launch_channel))
    loop.create_task(actualization_reader(actual_channel))
    loop.create_task(discovery_reader(pub, disc_channel))
    loop.create_task(kill_reader(pub, kill_channel))


loop.create_task(checks())
loop.create_task(server_discovery())
loop.create_task(handle_events())

loop.run_forever()

# is_server_running('glory.dota2classic.ru:27015')
