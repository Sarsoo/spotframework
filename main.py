import spotframework.net.user as userclass
import spotframework.net.playlist as playlist

if __name__ == '__main__':
    print('hello world')
    
    user = userclass.User()
    user.refreshToken()

    playlists = playlist.getPlaylists(user)

    for playlist in playlists:
        print(playlist['name'])

    print(len(playlists))
