import logging
from typing import List

from spotframework.model.track import TrackFull
from spotframework.model.uri import Uri
from spotframework.filter import get_track_objects

logger = logging.getLogger(__name__)


def deduplicate_by_id(tracks: List, include_malformed=True) -> List:
    prop = 'uri'

    return_tracks = []
    for inner_track, whole_track in zip(*get_track_objects(tracks)):
        if hasattr(inner_track, prop) and isinstance(getattr(inner_track, prop), Uri):
            if getattr(inner_track, prop) not in [getattr(i, prop) for i in return_tracks]:
                return_tracks.append(whole_track)
        else:
            if include_malformed:
                return_tracks.append(whole_track)

    return return_tracks


def deduplicate_by_name(tracks: List, include_malformed=True) -> List:
    return_tracks = []

    for inner_track, whole_track in zip(*get_track_objects(tracks)):
        if isinstance(inner_track, TrackFull):
            to_check_artists = [i.name.lower() for i in inner_track.artists]

            for index, (_inner_track, _whole_track) in enumerate(zip(*get_track_objects(return_tracks))):
                if inner_track.name.lower() == _inner_track.name.lower():

                    _track_artists = [i.name.lower() for i in _inner_track.artists]
                    if all((i in _track_artists for i in to_check_artists)):  # CHECK ARTISTS MATCH

                        # CHECK ALBUM TYPE, PREFER ALBUMS OVER SINGLES ETC
                        if inner_track.album.album_type.value > _inner_track.album.album_type.value:
                            logger.debug(f'better track source found, {inner_track} ({inner_track.album.album_type}) '
                                         f'> {_inner_track} ({_inner_track.album.album_type})')
                            return_tracks[index] = whole_track  # REPLACE
                        break  # FOUND, ESCAPE
            else:
                return_tracks.append(whole_track)  # NOT FOUND, ADD TO RETURN

        else:
            if include_malformed:
                return_tracks.append(whole_track)

    return return_tracks
