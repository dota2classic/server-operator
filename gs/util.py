import json

import socket
from srcds import srcds

RCON_PASSWORD = 'SPERMA5INACTION'


def get_port(ip: str) -> int:
    return int(ip.split(':')[1])


def get_this_host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host = s.getsockname()[0]
    s.close()
    return host


def execute_rcon(ip, command):
    server = srcds.SourceRcon(get_this_host(), get_port(ip), RCON_PASSWORD, 5)
    try:
        res = server.rcon(command)
        return True
    except Exception as e:
        return False
    finally:
        server.disconnect()


def is_server_running(ip):
    return execute_rcon(ip, 'echo a')
