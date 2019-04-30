import spotframework.net.user as userclass
import spotframework.net.network as networkclass
import spotframework.net.network as playlist

if __name__ == '__main__':
    print('hello world')

    network = networkclass.network(userclass.User())

    #network.getPlaylist('000Eh2vXzYGgrEFlgcWZj3')

    network.getPlayer()
