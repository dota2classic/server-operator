from config.servers import find_server
from gs.stop_server import stop_server
from aioredis import Redis


async def process_kill_requested_event(redis_queue: Redis, evt):
    server_url = evt['url']
    ip, server = find_server(server_url)
    stop_server(server)