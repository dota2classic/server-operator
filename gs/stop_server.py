from signal import SIGTERM
from typing import Dict, Any

from psutil import process_iter


# maybe consider rcon cmd quit?
def stop_server(server_info: Dict[str, Any]):
    port = server_info['port']
    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == port:
                proc.send_signal(SIGTERM)
