# import json
# from os import listdir, path, remove
# import subprocess
# import psutil
# from psutil import process_iter
# from signal import SIGTERM  # or SIGKILL
# import shutil
# import logging
# from threading import Timer
#
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)
#
#
#
# def kill_by_port(port):
#     for proc in process_iter():
#         for conns in proc.connections(kind='inet'):
#             if conns.laddr.port == port:
#                 proc.send_signal(SIGTERM)
#
#
#
#
# def clean_configurations(server):
#     basepath = '%s/dota/addons/sourcemod/plugins' % server
#     trash = [f for f in listdir(basepath) if path.isfile('%s/%s' % (basepath, f))]
#     for t in trash:
#         remove('%s/%s' % (basepath, t))
#
#
# def apply_configurations(server, configs):
#     clean_configurations(server)
#     for config in configs:
#         shutil.copy('./plugins/%s' % config, '%s/dota/addons/sourcemod/plugins/%s' % (server, config))
#
#
# def setup_teams(server, radiant, dire):
#     path = '%s/dota/addons/sourcemod/configs/teams.txt' % (server)
#     f = open(path, "w+")
#     content = '\n'.join(radiant) + '\n' + '\n'.join(dire) + '\n'
#     f.write(content)
#     f.close()
#     pass
#
#
#
#
# def run_server(server, game_mode):
#     for ip, p in supported_servers.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
#         if ip == server:
#             port = get_port(server)
#             load_count = 10
#             additional_config = ""
#             game_map = "dota"
#             if game_mode == 7:
#                 # diretide
#                 game_map = "dota_diretide_12"
#
#             if game_mode == 1:
#                 setup_sourcetv(p, ip)
#                 additional_config = "+exec server.cfg +tv_enable 1"
#
#             cmd = '%s/srcds.exe -console -maxplayers 14 -game dota -port %d +maxplayers 14 %s +map %s +dota_force_gamemode %d' % (
#             p, port, additional_config, game_map, game_mode)
#
#
#             process = subprocess.Popen(cmd)
#             if game_mode == 1:
#                 Timer(30.0, run_sourcetv, (process, p, port)).start()
#
#             return True
#
#     return False
#
#
#
# def start_server():
#     pass
#     data = request.get_json()
#     server = data['server']
#     config = data['config']
#     game_mode = config['map']
#     radiant = data.get('radiant')
#     dire = data.get('dire')
#     plugins = config['plugins']
#
#     if (radiant and dire):
#         setup_teams(supported_servers.get(server), radiant, dire)
#     apply_configurations(supported_servers.get(server), ['%s.smx' % t for t in plugins])
#
#     if server in supported_servers:
#         if is_port_open(get_port(server)):
#             return '', 400
#         if run_server(server, game_mode):
#             return '', 200
#         else:
#             return '', 400
#     return '', 401
