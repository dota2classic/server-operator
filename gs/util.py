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


def is_server_running(ip):
    server = srcds.SourceRcon(get_this_host(), get_port(ip), RCON_PASSWORD)
    try:
        res = server.rcon('status')
        # todo: some check
        return True
    except Exception as e:
        return False
    finally:
        server.disconnect()
