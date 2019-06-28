from spotframework.net.user import User
from spotframework.net.network import Network
import spotframework.log.log as log
import spotframework.net.const as const
import spotframework.io.json as json

import os
import datetime


def check_phone():

    response = os.system("ping -c 1 -w5 " + os.environ['PHONEIP'] + " > /dev/null 2>&1")
    log.log('checking for phone')
    if response == 0:
        return True
    else:
        return False


if __name__ == '__main__':

    try:

        network = Network(User())

        found = False

        for i in range(0, 36):
            if check_phone():
                found = True
                break

        if found:

            if os.path.exists(os.path.join(const.config_path, 'config.json')):
                data = json.load_json(os.path.join(const.config_path, 'config.json'))

                date = datetime.datetime.now()

                playlists = network.get_user_playlists()

                if data['alarm']['use_month']:
                    playlisturi = next((i.uri for i in playlists if i.name == date.strftime("%B %-y").lower()), data['alarm']['uri'])
                else:
                    playlisturi = data['alarm']['uri']

                network.play(playlisturi, network.get_device_id(data['alarm']['device_name']))

                network.set_shuffle(True)
                network.set_volume(data['alarm']['volume'])
                network.next()

        log.dump_log()

    except:
        log.dump_log()
