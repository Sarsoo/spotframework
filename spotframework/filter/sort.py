import logging
from typing import List
from datetime import datetime

from spotframework.model.album import SimplifiedAlbum
from spotframework.filter import get_track_objects

logger = logging.getLogger(__name__)


def sort_by_popularity(tracks: List, reverse: bool = False) -> List:
    prop = 'popularity'
    return [j for i, j
            in sorted([(k, l) for k, l in zip(*get_track_objects(tracks))
                       if hasattr(k, prop) and isinstance(getattr(k, prop), int)],
                      key=lambda x: x[0].popularity, reverse=reverse
                      )
            ]


def sort_by_release_date(tracks: List, reverse: bool = False) -> List:
    return [j for i, j
            in sorted([(k, l) for k, l in sort_artist_album_track_number(tracks, inner_tracks_only=False)
                       if hasattr(k, 'album') and isinstance(getattr(k, 'album'), SimplifiedAlbum)],
                      key=lambda x: x[0].album.release_date, reverse=reverse
                      )
            ]


def sort_by_added_date(tracks: List, reverse: bool = False) -> List:
    return [j for i, j
            in sorted([(k, l) for k, l in sort_artist_album_track_number(tracks, inner_tracks_only=False)
                       if hasattr(l, 'added_at') and isinstance(getattr(l, 'added_at'), datetime)],
                      key=lambda x: x[1].added_at,
                      reverse=reverse
                      )
            ]


def sort_artist_album_track_number(tracks: List, inner_tracks_only: bool = False) -> List:
    sorted_tracks = sorted([(i, w) for i, w in zip(*get_track_objects(tracks))
                            if hasattr(i, 'album') and isinstance(getattr(i, 'album'), SimplifiedAlbum)],
                           key=lambda x: (x[0].artists[0].name.lower(),
                                          x[0].album.name.lower(),
                                          x[0].track_number))
    if inner_tracks_only:
        return [i for i, w in sorted_tracks]

    return sorted_tracks

