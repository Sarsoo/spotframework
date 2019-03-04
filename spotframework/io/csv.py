import csv
import spotframework.net.playlist as playlistpull
import datetime

headers = ['name', 'artist', 'album', 'album artist', 'added', 'track id', 'album id', 'added by']

def exportPlaylist(user, playlistid, name, path):

    playlist = playlistpull.getPlaylistTracks(user, playlistid)

    with open('{}{}_{}.csv'.format(path, name.replace('/', '_'), str(datetime.datetime.now()).split('.')[0]), 'w') as fileobj:

        writer = csv.DictWriter(fileobj, fieldnames = headers)
        writer.writeheader()

        for track in playlist:

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
