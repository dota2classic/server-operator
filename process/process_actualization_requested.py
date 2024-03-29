from config.servers import find_server
from gs.util import is_server_running, execute_rcon


async def process_actualization_requested(event):
    try:
        ip, server = find_server(event['url'])

        is_running = is_server_running(ip)

        if is_running:
            execute_rcon(ip, 'd2c_session_sync')
        else:
            print('Server not runnning....')
            pass
            # await queue.publish_json('GameServerStoppedEvent', {
            #     'url': ip,
            #     'version': 'Dota_681'
            # })

    except:
        pass
        # print("There is no such server here, skipping actualization check")
