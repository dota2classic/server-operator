import subprocess



def run_sourcetv_relay(main_process: subprocess.Popen, path: str, game_port: int):
    relay_port = game_port + 5
    tv_port = game_port + 4
    cmd = "%s/srcds.exe -game dota -console +sv_hibernate_when_empty 1 +tv_port %d +tv_relay 127.0.0.1:%d +tv_relay_secret_code 0" % (
        path, relay_port, tv_port)

    relay_process = subprocess.Popen(cmd)
    # after main process is finished kill relay
    main_process.communicate()
    relay_process.kill()
