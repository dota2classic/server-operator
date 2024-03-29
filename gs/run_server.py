import json
import subprocess
from threading import Timer
from typing import Dict, Any

from config.config import MOCK_LAUNCH
from gs.util import RCON_PASSWORD
from gs.run_source_tv import run_sourcetv_relay
from gs.configure_server import configure_server
from gs.setup_source_tv import setup_source_tv


# export enum MatchmakingMode {
#   RANKED = 0,
#   UNRANKED = 1,
#   SOLOMID = 2,
#   DIRETIDE = 3,
#   GREEVILING = 4,
#   ABILITY_DRAFT = 5,
#   TOURNAMENT = 6,
# }

def get_map_for_mode(mode, version):
    if mode == 3:
        return 'dota_diretide_12'

    if version == 'Dota_681':
        return 'dota_training'
    elif version == 'Dota_684':
        return 'dota'

# export enum Dota_GameMode {
#   ALLPICK = 1,
#   CAPTAINS_MODE = 2,
#   RANDOM_DRAFT = 3,
#   SINGLE_DRAFT = 4,
#   ALL_RANDOM = 5,
#   // ?
#   DIRETIDE = 7,
#   REVERSE_CAPTAINS_MODE = 8,
#   GREEVILING = 9,
#   TUTORIAL = 10,
#   MID_ONLY = 11,
#   LEAST_PLAYED = 12,
#   LIMITED_HEROES = 13,
#   BALANCED_DRAFT = 17,
#   ABILITY_DRAFT = 18,
#
#   SOLOMID = 21,
#   RANKED_AP = 22
# }


def do_enable_tv(mode):
    return True
    return mode != 7


def get_game_mode_for_mode(mode, version):
    # ranked
    if mode == 0:
        if version == 'Dota_681':
            return 1
        elif version == 'Dota_684':
            return 22
    # unranked
    if mode == 1:
        return 1
    elif mode == 2:
        return 21
    elif mode == 9:
        return 21
    elif mode == 3:
        return 7
    elif mode == 4:
        return 9
    elif mode == 5:
        return 18
    elif mode == 6 or mode == 10:  # tournament 5x5 or captains mode
        return 2
    else:
        return 1


def get_srcds_path():
    import platform
    if platform.system() == "Linux":
        return "srcds.sh"

    elif platform.system() == "Windows":
        return "srcds.exe"


def run_server(ip: str, server_info: Dict[str, Any], match_id: int, match_info) -> bool:
    if MOCK_LAUNCH:
        return True

    print(json.dumps(server_info))
    port: int = server_info['port']
    additional_config = ""
    game_map = get_map_for_mode(match_info['mode'], match_info['version'])
    game_mode = get_game_mode_for_mode(
        match_info['mode'], match_info['version'])

#     enable_tv = False
    enable_tv = do_enable_tv(match_info['mode'])

    # if it's all pick or captains mode we enable source TV
    # if game_mode == 1 or game_mode == 2:
    if enable_tv:
        additional_config = "+exec server.cfg +tv_enable 1"
        setup_source_tv(server_info['path'], port)

    path = '%s/%s' % (server_info['path'], get_srcds_path())
    cmd = '-usercon -console -maxplayers 14 -game dota +rcon_password %s +ip 0.0.0.0 -port %d +maxplayers 14 %s +map %s +dota_force_gamemode %d' % (
        RCON_PASSWORD,
        port,
        additional_config,
        game_map,
        game_mode
    )

    # cmd = '%s/srcds.exe  -console -maxplayers 14 -game dota -port %d +maxplayers 14 %s +map %s +dota_force_gamemode %d' % (
    #     server_info['path'], port, additional_config, game_map, game_mode)

    configure_server(ip, server_info, match_id, match_info)

    fullcmd = [path] + cmd.split(' ')
    # print(cmd)
    process = subprocess.Popen(fullcmd)
    if enable_tv:
        # noinspection PyTypeChecker
        # Timer(30.0, run_sourcetv_relay, (process, server_info['path'], port)).start()
        Timer(5.0, run_sourcetv_relay,
              (process, server_info['path'], port)).start()

    return True
