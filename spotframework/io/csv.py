import csv
import spotframework.net.network as network
import datetime

headers = ['name', 'artist', 'album', 'album artist', 'added', 'track id', 'album id', 'added by']

def exportPlaylist(playlist, path, name=None):

    #playlist = network.getPlaylistTracks(user, playlistid)
    
    date = str(datetime.datetime.now())

    if name is None:
        name = playlist.name

    with open('{}/{}_{}.csv'.format(path, name.replace('/', '_'), date.split('.')[0]), 'w') as fileobj:

        writer = csv.DictWriter(fileobj, fieldnames = headers)
        writer.writeheader()

        for track in playlist.tracks:

            trackdict = {
                    'name':track['track']['name'],
                    'album':track['track']['album']['name'],
                    'added':track['added_at'],
                    'track id':track['track']['id'],
                    'album id':track['track']['album']['id'],
                    'added by':track['added_by']['id']}
            
            alart = []
            for albumartist in track['track']['album']['artists']:
                alart.append(albumartist['name'])

            trackdict['album artist'] = ', '.join(alart)

            art = []
            for artist in track['track']['artists']:
                art.append(artist['name'])

            trackdict['artist'] = ', '.join(art)

            writer.writerow(trackdict)
