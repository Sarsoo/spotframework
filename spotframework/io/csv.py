import csv
import datetime
import logging

logger = logging.getLogger(__name__)

headers = ['name', 'artist', 'album', 'album artist', 'added', 'track id', 'album id', 'artist id', 'added by']


def export_playlist(playlist, path, name=None):

    logger.info(f'{playlist.name} {path} {name}')
    
    date = str(datetime.datetime.now())

    if name is None:
        name = playlist.name

    with open('{}/{}_{}.csv'.format(path, name.replace('/', '_'), date.split('.')[0]), 'w', newline='') as fileobj:

        writer = csv.DictWriter(fileobj, fieldnames=headers)
        writer.writeheader()

        for track in playlist.tracks:
            writer.writerow({
                'name': track.track.name,
                'album': track.track.album.name,
                'added': track.added_at,
                'track id': track.track.uri.object_id if track.track.uri is not None else 'none',
                'album id': track.track.album.uri.object_id if track.track.album.uri is not None else 'none',
                'artist id': ', '.join(x.uri.object_id for x in track.track.artists),
                'added by': track.added_by.id,
                'album artist': ', '.join(x.name for x in track.track.album.artists),
                'artist': ', '.join(x.name for x in track.track.artists)
            })
