import spotframework.net.user as userclass
import spotframework.net.network as networkclass
import spotframework.log.log as log

import os
import datetime

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

        date = datetime.datetime.now()

        playlists = network.getUserPlaylists()

        playlisturi = next((i.uri for i in playlists if i.name == date.strftime("%B %-y").lower()), os.environ['SPOTALARMURI'])

        network.play(playlisturi, network.getDeviceID(os.environ['SPOTALARMDEVICENAME']))

        network.setShuffle(True)
        network.setVolume(os.environ['SPOTALARMVOLUME'])
        network.next()

    log.dumpLog()
