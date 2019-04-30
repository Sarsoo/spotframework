import spotframework.net.user as userclass
import spotframework.net.network as networkclass

import os

if __name__ == '__main__':
    network = networkclass.network(userclass.User())

    network.play(os.environ['SPOTALARMURI'], network.getDeviceID(os.environ['SPOTALARMDEVICENAME']))

    network.setShuffle(True)
    network.next()
