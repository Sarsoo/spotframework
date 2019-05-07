import spotframework.net.user as userclass
import spotframework.net.network as networkclass

import os

def checkPhone():

    response = os.system("ping -c 1 -w5 " + os.environ['PHONEIP'] + " > /dev/null 2>&1")
    print('checking for phone')
    if response == 0:
        return True
    else:
        return False

if __name__ == '__main__':
    network = networkclass.network(userclass.User())

    found = False

    for i in range(0, 36):
        if checkPhone():
            found = True
            break

    if found:
        network.play(os.environ['SPOTALARMURI'], network.getDeviceID(os.environ['SPOTALARMDEVICENAME']))

        network.setShuffle(True)
        network.setVolume(os.environ['SPOTALARMVOLUME'])
        network.next()
