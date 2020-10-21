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

from aioredis import Redis

from gs.run_server import run_server
from config.servers import find_server


async def process_match_created_event(redis_queue: Redis, evt):
    print("Processing MatchCreatedEvent")
    try:
        ip, server = find_server(evt['url'])

        good = run_server(server, evt['info']['mode'])

        if good:
            server['down_for'] = 0
            server.pop('down_since', None)
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
