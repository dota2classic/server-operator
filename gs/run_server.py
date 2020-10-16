import subprocess
from threading import Timer
from typing import Dict, Any

from gs import run_source_tv
from gs.setup_source_tv import setup_source_tv


def run_server(server_info: Dict[str, Any], game_mode: int) -> bool:
    port: int = server_info['port']
    additional_config = ""
    game_map = "dota"
    if game_mode == 7:
        # diretide
        game_map = "dota_diretide_12"

    if game_mode == 1:
        additional_config = "+exec server.cfg +tv_enable 1"

    cmd = '%s/srcds.exe -console -maxplayers 14 -game dota -port %d +maxplayers 14 %s +map %s +dota_force_gamemode %d' % (
        server_info['path'], port, additional_config, game_map, game_mode)


    # todo remove
    return True
    # print(cmd)
    process = subprocess.Popen(cmd)
    if game_mode == 1:
        setup_source_tv(server_info['path'], port)
        # noinspection PyTypeChecker
        Timer(30.0, run_source_tv, (process, server_info['path'], port)).start()

    return True