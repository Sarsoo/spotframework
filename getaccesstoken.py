from spotframework.net.user import User
from spotframework.net.network import Network

if __name__ == '__main__':

    network = Network(User())

    print(network.user.access_token)
