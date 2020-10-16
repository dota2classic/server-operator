import json

from flask import Flask, request
from redis import Redis

flask_app = Flask(__name__)

flask_redis_queue =  Redis('localhost', 6379)



@flask_app.route('/update_state', methods=['POST'])
def update_game_state():
    data = request.get_json()
    flask_redis_queue.publish('GameSessionUpdatedEvent', json.dumps({
        'matchId': data['match_id'],
        'state': data['state'],
        'url': data['url'],
    }))
    return '', 200



@flask_app.route('/finish_match', methods=['POST'])
def update_game_state():
    data = request.get_json()
    flask_redis_queue.publish('MatchFinishedEvent', json.dumps({
        'matchId': data['match_id']
    }))
    return '', 200


