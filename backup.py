import spotframework.net.user as userclass
import spotframework.net.network as networkclass
import spotframework.io.csv as csvwrite
import spotframework.log.log as log

import sys
import datetime
import os

if __name__ == '__main__':

    network = networkclass.network(userclass.User())
    playlists = network.getUserPlaylists()

    for playlist in playlists:
        playlist.tracks = network.getPlaylistTracks(playlist.playlistid)
    
    path = sys.argv[1]
    
    datepath = str(datetime.datetime.now()).split(' ')[0].replace('-', '/')

    totalpath = os.path.join(path, datepath)
    pathdir = os.path.dirname(totalpath)
    if not os.path.exists(totalpath):
        os.makedirs(totalpath)

    for play in playlists:
        csvwrite.exportPlaylist(play, totalpath)

    log.dumpLog()
