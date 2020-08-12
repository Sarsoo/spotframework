from spotframework.net.user import NetworkUser
from spotframework.net.network import Network, SpotifyNetworkException
import spotframework.io.csv as csvwrite

import sys
import datetime
import os
import logging

if __name__ == '__main__':

    logger = logging.getLogger('spotframework')

    file_handler = logging.FileHandler(".spot/backup.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s:%(funcName)s - %(message)s'))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(name)s:%(funcName)s - %(message)s'))
    logger.addHandler(stream_handler)

    datepath = str(datetime.datetime.now()).split(' ')[0].replace('-', '/')

    totalpath = os.path.join(sys.argv[1], datepath)
    if not os.path.exists(totalpath):
        logger.info(f'creating path {totalpath}')
        os.makedirs(totalpath)

    network = Network(NetworkUser(client_id=os.environ['SPOT_CLIENT'],
                                  client_secret=os.environ['SPOT_SECRET'],
                                  refresh_token=os.environ['SPOT_REFRESH'])).refresh_access_token()

    try:
        playlists = network.user_playlists()

        for playlist in playlists:
            try:
                playlist.tracks = network.playlist_tracks(uri=playlist.uri)
                csvwrite.export_playlist(playlist, totalpath)
            except SpotifyNetworkException:
                logger.exception(f'error occured during {playlist.name} track retrieval')

    except SpotifyNetworkException:
        logger.exception('error occured during user playlists retrieval')
