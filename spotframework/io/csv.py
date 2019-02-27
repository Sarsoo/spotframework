import csv
import spotframework.net.playlist as playlistpull

headers = ['name', 'artist', 'album', 'album artist', 'added', 'spotify id', 'added by']

def exportPlaylist(user, playlistid):

    playlist = playlistpull.getPlaylistTracks(user, playlistid)

    with open('out.csv', 'w') as fileobj:

        writer = csv.DictWriter(fileobj, fieldnames = headers)
        writer.writeheader()

        for track in playlist:

            trackdict = {
                    'name':track['track']['name'],
                    'album':track['track']['album']['name'],
                    'added':track['added_at'],
                    'spotify id':track['track']['id'],
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
