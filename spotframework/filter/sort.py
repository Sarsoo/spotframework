import logging
from typing import List

from spotframework.model.track import Track

logger = logging.getLogger(__name__)


def sort_by_popularity(tracks: List, reverse: bool = False, include_malformed=False) -> List:
    prop = 'popularity'

    return_tracks = sorted([i for i in tracks if hasattr(i, prop) and isinstance(getattr(i, prop), int)],
                           key=lambda x: x.popularity, reverse=reverse)

    if include_malformed:
        return_tracks += [i for i in tracks
                          if not hasattr(i, prop)
                          or (hasattr(i, prop) and not isinstance(getattr(i, prop), int))]

    return return_tracks


def sort_by_release_date(tracks: List, reverse: bool = False) -> List:
    return sorted(sort_artist_album_track_number(tracks),
                  key=lambda x: x.album.release_date, reverse=reverse)


def sort_by_artist_name(tracks: List, reverse: bool = False) -> List:
    return_tracks = sorted([i for i in tracks if isinstance(i, Track)],
                           key=lambda x: (x.album.name.lower(),
                                          x.track_number))
    return_tracks.sort(key=lambda x: x.artists[0].name.lower(), reverse=reverse)
    return return_tracks


def sort_by_added_date(tracks: List, reverse: bool = False) -> List:
    return sorted(sort_artist_album_track_number(tracks),
                  key=lambda x: x.added_at,
                  reverse=reverse)


def sort_artist_album_track_number(tracks: List) -> List:
    return sorted([i for i in tracks if isinstance(i, Track)],
                  key=lambda x: (x.artists[0].name.lower(),
                                 x.album.name.lower(),
                                 x.track_number))

