# export class MatchInfo {
#   constructor(
#     public readonly mode: MatchmakingMode,
#     public readonly roomId: string,
#     public readonly radiant: PlayerId[],
#     public readonly dire: PlayerId[],
#     public readonly averageMMR: number,
#     public readonly version: Dota2Version
#   ) {}
# }

# export class MatchCreatedEvent {
#   constructor(
#     public readonly id: number,
#     public readonly url: string,
#     public readonly info: MatchInfo
#   )
# }


# export class GameServerStartedEvent {
#   constructor(
#     public readonly matchId: number,
#     public readonly info: MatchInfo,
#   ) {}
# }
import asyncio

from aioredis import Redis

from gs.run_server import run_server
from config.servers import find_server
from gs.util import is_server_running


async def process_match_created_event(redis_queue: Redis, evt):
    print("Processing MatchCreatedEvent")
    try:
        ip, server = find_server(evt['url'])

        is_running = is_server_running(ip)

        if is_running:
            # we dont wanna start useless server
            await redis_queue.publish_json('GameServerNotStartedEvent', ({
                'matchId': evt['matchId'],
                'info': evt['info'],
                'url': ip
            }))
            return
        good = run_server(ip, server, evt['matchId'], evt['info'])

        if good:
            server['down_for'] = 0
            server.pop('down_since', None)



            # todo: emit this from plugin maybe?
            await redis_queue.publish_json('GameServerStartedEvent', ({
                'matchId': evt['matchId'],
                'info': evt['info'],
                'url': ip
            }))


        else:
            await redis_queue.publish_json('GameServerNotStartedEvent', ({
                'matchId': evt['matchId'],
                'info': evt['info'],
                'url': ip
            }))
    except ValueError:
        print("There is no such server here, skipping")
