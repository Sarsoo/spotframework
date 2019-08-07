from  spotframework.net.user import User
from  spotframework.net.network import Network
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

    try:

        network = Network(User(os.environ['SPOTCLIENT'],
                               os.environ['SPOTSECRET'],
                               os.environ['SPOTACCESS'],
                               os.environ['SPOTREFRESH']))
        playlists = network.get_user_playlists()

        for playlist in playlists:
            playlist.tracks = network.get_playlist_tracks(playlist.playlistid)

        path = sys.argv[1]

        datepath = str(datetime.datetime.now()).split(' ')[0].replace('-', '/')

        totalpath = os.path.join(path, datepath)
        pathdir = os.path.dirname(totalpath)
        if not os.path.exists(totalpath):
            os.makedirs(totalpath)

        for play in playlists:
            csvwrite.export_playlist(play, totalpath)

    except Exception as e:
        logger.exception(f'exception occured')
