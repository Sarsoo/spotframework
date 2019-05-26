import spotframework.net.user as userclass
import spotframework.net.network as networkclass

if __name__ == '__main__':

    network = networkclass.network(userclass.User())

    print(network.user.access_token)
