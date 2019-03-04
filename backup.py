import spotframework.net.user as userclass
import spotframework.net.playlist as playlist
import spotframework.io.csv as csvwrite

import sys

if __name__ == '__main__':

    user = userclass.User()

    playlists = playlist.getUserPlaylists(user)

    for play in playlists:
        csvwrite.exportPlaylist(user, play['id'], play['name'], sys.argv[1])
        print(play['name'] + ' exported')
