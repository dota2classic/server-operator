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
import json

from aioredis import Redis

from gs.run_server import run_server
from servers import supported_servers


async def process_match_created_event(redis_queue: Redis, evt):
    print("haha event goes brr")

    for ip, p in supported_servers.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if ip == evt['url']:
            good = run_server(p, evt['info']['mode'])
            if good:
                await redis_queue.publish_json('GameServerStartedEvent', ({
                    'matchId': evt['matchId'],
                    'info': evt['info']
                }))

            break
