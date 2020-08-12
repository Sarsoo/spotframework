import logging
from typing import Generator, Union, List
from datetime import datetime

from spotframework.model.track import PlaylistTrack, LibraryTrack

logger = logging.getLogger(__name__)


def added_before(tracks: List, boundary: datetime, include_malformed=True) -> Generator[Union[PlaylistTrack,
                                                                                              LibraryTrack],
                                                                                        None, None]:
    prop = 'added_at'

    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), datetime):
            if getattr(track, prop) < boundary:
                yield track
        else:
            if include_malformed:
                yield track



def added_after(tracks: List, boundary: datetime, include_malformed=True) -> Generator[Union[PlaylistTrack,
                                                                                              LibraryTrack],
                                                                                        None, None]:
    prop = 'added_at'

    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), datetime):
            if getattr(track, prop) > boundary:
                yield track
        else:
            if include_malformed:
                yield track
