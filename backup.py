from spotframework.net.user import NetworkUser
from spotframework.net.network import Network, SpotifyNetworkException
import spotframework.io.csv as csvwrite

import sys
import datetime
import os
import logging

if __name__ == '__main__':

    logger = logging.getLogger('spotframework')

    log_format = '%(asctime)s %(levelname)s %(name)s:%(funcName)s - %(message)s'

    file_handler = logging.FileHandler(".spot/backup.log")
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    stream_log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
    stream_formatter = logging.Formatter(stream_log_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(stream_handler)

    # try:

    network = Network(NetworkUser(client_id=os.environ['SPOT_CLIENT'],
                                  client_secret=os.environ['SPOT_SECRET'],
                                  refresh_token=os.environ['SPOT_REFRESH'])).refresh_access_token()

    try:
        playlists = network.get_user_playlists(response_limit=5)

        for playlist in playlists:
            try:
                playlist.tracks = network.get_playlist_tracks(playlist.uri)
            except SpotifyNetworkException:
                logger.exception(f'error occured during {playlist.name} track retrieval')

        path = sys.argv[1]

        datepath = str(datetime.datetime.now()).split(' ')[0].replace('-', '/')

        totalpath = os.path.join(path, datepath)
        pathdir = os.path.dirname(totalpath)
        if not os.path.exists(totalpath):
            os.makedirs(totalpath)

        for play in playlists:
            csvwrite.export_playlist(play, totalpath)

    except SpotifyNetworkException:
        logger.exception('error occured during user playlist retrieval')

    # except Exception as e:
    #     logger.exception(f'exception occured')
