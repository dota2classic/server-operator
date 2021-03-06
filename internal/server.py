import json

from flask import Flask, request
from redis import Redis

from config.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

flask_app = Flask(__name__)

flask_redis_queue = Redis(REDIS_HOST, REDIS_PORT, password=REDIS_PASSWORD)



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




@flask_app.route('/steam_lag_report', methods=['POST'])
def steam_lag_report():
    data = request.get_json()
    flask_redis_queue.publish('SteamLagReportedEvent', json.dumps(data))
    return '', 200

@flask_app.route('/session_sync', methods=['POST'])
def session_sync():
    data = request.get_json()
    flask_redis_queue.publish('ServerSessionSyncEvent', json.dumps(data))
    return '', 200


@flask_app.route('/report_did_not_load', methods=['POST'])
def report_did_not_load():
    data = request.get_json()

    for p in data['players']:
        flask_redis_queue.publish('PlayerNotLoadedEvent', json.dumps({
            'matchId': data['matchId'],
            'playerId': {
                'value': p
            }
        }))
    return '', 200


#
# @flask_app.route('/start_match', methods=['POST'])
# def finish_match():
#     data = request.get_json()
#     flask_redis_queue.publish('MatchFinishedEvent', json.dumps({
#         'matchId': data['match_id']
#     }))
#     return '', 200


@flask_app.route('/finish_match', methods=['POST'])
def finish_match():
    data = request.get_json()
    flask_redis_queue.publish('MatchFinishedEvent', json.dumps({
        'matchId': data['match_id']
    }))
    return '', 200


@flask_app.route('/live_match', methods=['POST'])
def live_match():
    data = request.get_json()
    flask_redis_queue.publish('LiveMatchUpdateEvent', json.dumps(data))
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

@flask_app.route('/match_results', methods=['POST'])
def match_results():
    # ok let's keep it simple and let plugin form json lul
    data = request.get_json()
    flask_redis_queue.publish('GameResultsEvent', json.dumps(data))
    return '', 200

