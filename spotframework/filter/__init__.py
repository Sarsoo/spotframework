from typing import List


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
