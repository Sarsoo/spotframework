import spotframework.net.user as userclass
import spotframework.net.playlist as playlist

if __name__ == '__main__':
    print('hello world')
    
    user = userclass.User()

    playlists = playlist.getPlaylists(user)

    #for playlister in playlists:
        #print(playlister['name'])

    print(playlists[0])
    #print(len(playlists))

    print(user.username)

    moreplaylists = playlist.getUserPlaylists(user)
    print(len(moreplaylists))
