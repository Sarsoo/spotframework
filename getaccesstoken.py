from spotframework.net.user import User
from spotframework.net.network import Network

import os

if __name__ == '__main__':

    network = Network(User(os.environ['SPOTCLIENT'],
                           os.environ['SPOTSECRET'],
                           os.environ['SPOTACCESS'],
                           os.environ['SPOTREFRESH']))

    print(network.user.access_token)
