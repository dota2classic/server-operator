from gs.util import get_port, RCON_PASSWORD


def setup_source_tv(path: str, server_port: int) -> None:
    path = '%s/dota/cfg/server.cfg' % path
    f = open(path, "w+")
    source_tv_port = server_port + 4
    # 27015 -> 27019 SourceTV
    # 27015 -> 27020 SourceTV Relay
    content = """sv_hibernate_when_empty 0
tv_maxclients 16 // max source tv clients
tv_name Dota2Classic TV
tv_delay 0 // delay in seconds for watching the game
tv_port {} // source tv port
tv_autorecord 0 // automatically records every game
tv_secret_code 0""".format(source_tv_port)
    f.write(content)
    f.close()
