from spotframework.net.user import NetworkUser
from spotframework.net.network import Network
import spotframework.net.const as const
import spotframework.io.json as json
import spotframework.util.monthstrings as month

import os
import datetime
import logging


logger = logging.getLogger('spotframework')

file_log_format = '%(asctime)s %(levelname)s %(name)s:%(funcName)s - %(message)s'

file_handler = logging.FileHandler(".spot/alarm.log")
file_formatter = logging.Formatter(file_log_format)
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)

stream_log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
stream_formatter = logging.Formatter(stream_log_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

logger.addHandler(stream_handler)


def check_phone():

    response = os.system("ping -c 1 -w5 " + os.environ['PHONEIP'] + " > /dev/null 2>&1")
    logger.info('checking for phone')
    if response == 0:
        return True
    else:
        return False


if __name__ == '__main__':

    try:
        network = Network(NetworkUser(client_id=os.environ['SPOT_CLIENT'],
                                      client_secret=os.environ['SPOT_SECRET'],
                                      refresh_token=os.environ['SPOT_REFRESH'])).refresh_access_token()

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
                    playlisturi = next((i.uri for i in playlists if i.name == month.get_this_month()),
                                       data['alarm']['uri'])
                else:
                    playlisturi = data['alarm']['uri']

                network.play(uri=playlisturi, deviceid=network.get_device_id(data['alarm']['device_name']))

                network.set_shuffle(True)
                network.set_volume(data['alarm']['volume'])
                network.next()

    except Exception as e:
        logger.exception('exception occured')
