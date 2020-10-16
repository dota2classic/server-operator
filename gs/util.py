import json

from srcds import srcds

RCON_PASSWORD = ''

def get_port(ip: str) -> int:
    return int(ip.split(':')[1])


def is_server_running(ip):
    server = srcds.SourceRcon('127.0.0.1', get_port(ip), RCON_PASSWORD)
    try:
        res = json.loads(server.rcon('info'))
        # todo: some check
        return True
    except:
        return False
    finally:
        server.disconnect()
