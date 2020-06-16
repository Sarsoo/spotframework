import logging
from typing import List

from spotframework.model.track import SpotifyTrack
from spotframework.model.album import SpotifyAlbum
from spotframework.model.uri import Uri

logger = logging.getLogger(__name__)


def deduplicate_by_id(tracks: List, include_malformed=True) -> List:
    prop = 'uri'

    return_tracks = []
    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), Uri):
            if getattr(track, prop) not in [getattr(i, prop) for i in return_tracks]:
                return_tracks.append(track)
        else:
            if include_malformed:
                return_tracks.append(track)

    return return_tracks


def deduplicate_by_name(tracks: List, include_malformed=True) -> List:
    return_tracks = []

    for track in tracks:
        if isinstance(track, SpotifyTrack):
            to_check_artists = [i.name.lower() for i in track.artists]

            for index, _track in enumerate(return_tracks):
                if track.name.lower() == _track.name.lower():

                    _track_artists = [i.name.lower() for i in _track.artists]
                    if all((i in _track_artists for i in to_check_artists)):  # CHECK ARTISTS MATCH

                        if not isinstance(track.album, SpotifyAlbum):
                            logger.warning(f'{track.name} album not of type SpotifyAlbum')
                            continue

                        if not isinstance(_track.album, SpotifyAlbum):
                            logger.warning(f'{_track.name} album not of type SpotifyAlbum')
                            continue

                        # CHECK ALBUM TYPE, PREFER ALBUMS OVER SINGLES ETC
                        if track.album.album_type.value > _track.album.album_type.value:
                            logger.debug(f'better track source found, {track} ({track.album.album_type}) '
                                         f'> {_track} ({_track.album.album_type})')
                            return_tracks[index] = track  # REPLACE
                        break  # FOUND, ESCAPE
            else:
                return_tracks.append(track)  # NOT FOUND, ADD TO RETURN

        else:
            if include_malformed:
                return_tracks.append(track)

    return return_tracks
