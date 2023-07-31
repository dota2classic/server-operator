import subprocess


def get_srcds_path():
    import platform
    if platform.system() == "Linux":
        return "srcds.sh"

    elif platform.system() == "Windows":
        return "srcds.exe"


def hard_kill(process):
    import os
    import signal
    if os.name == 'nt':  # windows
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=process.pid))
    else:
        os.kill(process.pid, signal.SIGTERM)

def run_sourcetv_relay(main_process: subprocess.Popen, path: str, game_port: int):
    relay_port = game_port + 5
    tv_port = game_port + 4

    path = '%s/%s' % (path, get_srcds_path())
    print("%d port of source tv", relay_port)
    cmd = "-game dota -console +sv_hibernate_when_empty 1 +tv_port %d +tv_relay 127.0.0.1:%d +tv_relay_secret_code 0" % (relay_port, tv_port)



    fullcmd = [path] + cmd.split(' ')

    relay_process = subprocess.Popen(fullcmd)
    # after main process is finished kill relay
    print("Waiting for main_process to finish...")
    main_process.communicate()

    print("MAIN process died, kill relay!")
    hard_kill(relay_process)
#     relay_process.terminate()
