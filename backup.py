from  spotframework.net.user import User
from  spotframework.net.network import Network
import spotframework.io.csv as csvwrite
import spotframework.log.log as log

import sys
import datetime
import os

if __name__ == '__main__':

    try:

        network = Network(User())
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

        log.dump_log()

    except:
        log.dump_log()
