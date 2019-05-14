import csv
import datetime

import spotframework.log.log as log

headers = ['name', 'artist', 'album', 'album artist', 'added', 'track id', 'album id', 'added by']

def exportPlaylist(playlist, path, name=None):

    log.log('exportPlaylist', playlist.name, path, name)
    
    date = str(datetime.datetime.now())

    if name is None:
        name = playlist.name

    with open('{}/{}_{}.csv'.format(path, name.replace('/', '_'), date.split('.')[0]), 'w', newline='') as fileobj:

        writer = csv.DictWriter(fileobj, fieldnames=headers)
        writer.writeheader()

        for track in playlist.tracks:

            trackdict = {
                    'name':track['track']['name'],
                    'album':track['track']['album']['name'],
                    'added':track['added_at'],
                    'track id':track['track']['id'],
                    'album id':track['track']['album']['id'],
                    'added by':track['added_by']['id']}

            trackdict['album artist'] = ', '.join(x['name'] for x in track['track']['album']['artists'])

            trackdict['artist'] = ', '.join(x['name'] for x in track['track']['artists'])

            writer.writerow(trackdict)
