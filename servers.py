import json
from os import listdir

supported_servers = {}

with open("./serverlist.json") as json_file:
    supported_servers = json.load(json_file)


configuration_list = listdir("./plugins")