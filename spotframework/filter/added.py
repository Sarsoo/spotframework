import logging
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)


def added_before(tracks: List, boundary: datetime, include_malformed=True) -> List:
    prop = 'added_at'

    return_tracks = []
    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), datetime):
            if getattr(track, prop) < boundary:
                return_tracks.append(track)
        else:
            if include_malformed:
                return_tracks.append(track)

    return return_tracks


def added_after(tracks: List, boundary: datetime, include_malformed=True) -> List:
    prop = 'added_at'

    return_tracks = []
    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), datetime):
            if getattr(track, prop) > boundary:
                return_tracks.append(track)
        else:
            if include_malformed:
                return_tracks.append(track)

    return return_tracks
