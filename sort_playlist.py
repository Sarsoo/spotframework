from spotframework.net.network import Network
from spotframework.net.user import NetworkUser
from spotframework.engine.playlistengine import PlaylistEngine

import os
import logging
import sys


logger = logging.getLogger('spotframework')

log_format = '%(asctime)s %(levelname)s %(name)s - %(funcName)s - %(message)s'

file_handler = logging.FileHandler(".spot/sort_playlist.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

stream_log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
stream_formatter = logging.Formatter(stream_log_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

logger.addHandler(stream_handler)


def go(playlist_name):

    net = Network(NetworkUser(os.environ['SPOTCLIENT'],
                              os.environ['SPOTSECRET'],
                              os.environ['SPOTREFRESH']))
    net.user.refresh_access_token()

    engine = PlaylistEngine(net)
    engine.reorder_playlist_by_added_date(playlist_name)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        name = sys.argv[1]
        if len(sys.argv) > 2:
            for i in sys.argv[2:]:
                name += ' ' + i
        go(sys.argv[1])
    else:
        name = input('enter playlist name: ')
        if name == '':
            exit()
        go(name)
