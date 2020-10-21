import json

from flask import Flask, request
from redis import Redis

from config.config import REDIS_HOST, REDIS_PORT

flask_app = Flask(__name__)

flask_redis_queue = Redis(REDIS_HOST, REDIS_PORT)



# todo?
# @flask_app.route('/update_state', methods=['POST'])
# def update_game_state():
#     data = request.get_json()
#     flask_redis_queue.publish('GameSessionUpdatedEvent', json.dumps({
#         'matchId': data['match_id'],
#         'state': data['state'],
#         'url': data['url'],
#     }))
#     return '', 200





@flask_app.route('/finish_match', methods=['POST'])
def finish_match():
    data = request.get_json()
    flask_redis_queue.publish('MatchFinishedEvent', json.dumps({
        'matchId': data['match_id']
    }))
    return '', 200



# export interface PlayerInMatchDTO {
#   readonly steam_id: string;
#   readonly team: number;
#   readonly kills: number;
#   readonly deaths: number;
#   readonly assists: number;
#   readonly level: number;
#   readonly items: string[];
#   readonly gpm: number;
#   readonly xpm: number;
#   readonly last_hits: number;
#   readonly denies: number;
#
#   readonly hero: string;
# }
#
# export class GameResultsEvent {
#   constructor(
#     public readonly matchId: number,
#     public readonly radiantWin: boolean,
#     public readonly duration: number,
#     public readonly type: MatchmakingMode,
#     public readonly timestamp: number,
#     public readonly server: string,
#     public readonly players: PlayerInMatchDTO[],
#   ) {}
# }

@flask_app.route('/finish_match', methods=['POST'])
def match_results():
    # ok let's keep it simple and let plugin form json lul
    data = request.get_json()
    flask_redis_queue.publish('MatchFinishedEvent', json.dumps(data))
    return '', 200

