import json
from os import listdir, path, remove
from typing import Dict, Any


def clean_configurations(server_info: Dict[str, Any]):
    basepath = '%s/dota/addons/sourcemod/plugins' % server_info['path']
    trash = [f for f in listdir(basepath) if path.isfile('%s/%s' % (basepath, f))]
    for t in trash:
        remove('%s/%s' % (basepath, t))


def load_match_info(ip: str, server_info: Dict[str, Any], match_id, match_info):
    file_path = '%s/dota/addons/sourcemod/configs/match.json' % server_info['path']
    f = open(file_path, "w+")
    config = {
        'matchId': match_id,
        'radiant': [t['value'] for t in match_info['radiant']],
        'dire': [t['value'] for t in match_info['dire']],
        'server_url': ip,
        'mode': match_info['mode']
    }

    f.write(json.dumps(config))
    f.close()


def configure_server(ip: str, server_info: Dict[str, Any], match_id: int, match_info):
    clean_configurations(server_info)
    load_match_info(ip, server_info, match_id, match_info)
