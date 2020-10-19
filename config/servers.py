import json
from os import listdir

supported_servers = {}

with open("./serverlist.json") as json_file:
    supported_servers = json.load(json_file)



def find_server(url):
    for ip, p in supported_servers.items():
        if ip == url:
            return ip, url
    return None


configuration_list = listdir("./plugins")