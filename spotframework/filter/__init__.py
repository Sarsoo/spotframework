from typing import List, Union, Generator, Tuple
import logging
from spotframework.model.track import SimplifiedTrack, LibraryTrack, PlayedTrack, PlaylistTrack

logger = logging.getLogger(__name__)


def remove_local(tracks: List, include_malformed=True) -> Generator[SimplifiedTrack, None, None]:
    prop = 'is_local'

    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), bool):
            if getattr(track, prop) is False:
                yield track
        else:
            if include_malformed:
                yield track


def get_track_objects(tracks: List) -> Generator[Tuple[SimplifiedTrack, Union[SimplifiedTrack,
                                                                              PlaylistTrack,
                                                                              PlayedTrack,
                                                                              LibraryTrack]], None, None]:
    for track in tracks:
        if isinstance(track, SimplifiedTrack):
            yield track, track
        elif isinstance(track, (PlaylistTrack, PlayedTrack, LibraryTrack)):
            yield track.track, track
        else:
            logger.warning(f'invalid type found for {track} ({type(track)}), discarding')
