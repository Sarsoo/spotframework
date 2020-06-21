from typing import List
import logging
from spotframework.model.track import SimplifiedTrack, LibraryTrack, PlayedTrack, PlaylistTrack

logger = logging.getLogger(__name__)


def remove_local(tracks: List, include_malformed=True) -> List:
    prop = 'is_local'

    return_tracks = []
    for track in tracks:
        if hasattr(track, prop) and isinstance(getattr(track, prop), bool):
            if getattr(track, prop) is False:
                return_tracks.append(track)
        else:
            if include_malformed:
                return_tracks.append(track)

    return return_tracks


def get_track_objects(tracks: List) -> (List, List):

    inner_tracks = []
    whole_tracks = []
    for track in tracks:
        if isinstance(track, SimplifiedTrack):
            inner_tracks.append(track)
            whole_tracks.append(track)
        elif isinstance(track, (PlaylistTrack, PlayedTrack, LibraryTrack)):
            inner_tracks.append(track.track)
            whole_tracks.append(track)
        else:
            logger.warning(f'invalid type found for {track} ({type(track)}), discarding')

    return inner_tracks, whole_tracks
