import spotframework.net.user as userclass
import spotframework.net.playlist as playlist
import spotframework.io.csv as csvwrite

if __name__ == '__main__':

    user = userclass.User()

    playlists = playlist.getPlaylists(user)

    for play in playlists:
        csvwrite.exportPlaylist(user, play['id'], play['name'])
