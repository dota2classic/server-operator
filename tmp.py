import json
import subprocess
import time
from datetime import datetime

import socketio
import os
import asyncio
# import requests
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_config():
    data = {}
    try:
        with open("C:\dota2classic.com\scripts\config.json", "r") as read_file:
            data = json.load(read_file)
    except Exception:
        pass
    return data

config = get_config()
name = config.get("name", "unknown")
master_server_url = config.get("master_server_url", 'http://localhost:8080')

class VpsClientNamespace(socketio.AsyncClientNamespace):
    async def on_connect(self):
        print('connection established')
        await self.auth()

    async def auth(self):
        async def auth_callback(auth_res):
            if auth_res:
                print('auth')
        await self.emit('auth', name, callback=auth_callback)

    async def on_disconnect(self):
        print('disconnected from server')

    async def on_request_processes(self, data):  # should equal emit("message", data)
        print("3 accept request and respond")
        pids = get_process_id("srcds")
        await self.emit('active_processes', {'pids': pids, 'name': name}, namespace='/vps')

    async def on_request_start_dedicated(self, data):
        pid = start_dedicated(data)
        # return data["server_name"], data["match_id"], pid

    async def on_request_restart_dedicated(self, data):
        terminate_dedicated(data["pid"])
        pid = start_dedicated(data)
        return data["server_name"], data["match_id"], pid

    async def on_request_stop_dedicated(self, data):
        terminate_dedicated(data["pid"])


def start_dedicated(data):
    data += " -tickrate 128"
    subprocess.Popen(data, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def terminate_dedicated(pid):
    subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)])


def wait_until_true(func, timeout, interval):
    time_left = 0
    while time_left < timeout:
        if func():
            return
        time_left += interval
        time.sleep(interval)


def get_process_id_by_createtime(name):
    get_unix_timestamp = lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M:%S')
    process_info = get_process_info(name,
    "id,  @{Name='starttime';Expression={Get-Date $_.starttime -Format 'dd.MM.yyyy HH:mm:ss'}}")
    result_list = [row.split(" ", 1) for row in process_info]
    result = {get_unix_timestamp(l[1]).timestamp(): int(l[0]) for l in result_list}
    return result


def get_process_id(name):
    process_info = get_process_info(name, "id")
    result = [int(id) for id in process_info]
    return result


def get_process_info(name, fields):
    result = subprocess.run(["powershell.exe",  f"Get-Process {name} | select {fields}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.stderr:
        return []

    result_string = result.stdout.decode(encoding='UTF-8')
    result_list = [row.strip() for row in result_string.splitlines() if row.strip()][2:]
    return result_list



async def main():
    sio = socketio.AsyncClient(ssl_verify=False)
    sio.register_namespace(VpsClientNamespace('/vps'))
    while True:
        try:
            print(master_server_url)
            await sio.connect(master_server_url, transports="websocket" )
            break
        except socketio.exceptions.ConnectionError as e:
            print("connection error, retrying..")
            await asyncio.sleep(3)
    await sio.wait()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
