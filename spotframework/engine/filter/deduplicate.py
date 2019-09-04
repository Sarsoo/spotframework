from spotframework.engine.filter.abstract import AbstractProcessor
from typing import List
from spotframework.model.track import Track, SpotifyTrack


class DeduplicateByID(AbstractProcessor):

    def __init__(self,
                 names: List[str] = None,
                 keep_malformed_type: bool = True):
        super().__init__(names)
        self.keep_malformed_type = keep_malformed_type

    def process(self, tracks: List[Track]):
        return_tracks = []
        malformed_tracks = []

        for track in tracks:
            if isinstance(track, SpotifyTrack):
                if track.uri not in [i.uri for i in return_tracks]:
                    return_tracks.append(track)
            else:
                malformed_tracks.append(track)

        if self.keep_malformed_type:
            return_tracks += malformed_tracks

        return return_tracks


class DeduplicateByName(AbstractProcessor):

    def process(self, tracks: List[Track]):
        return_tracks = []

        for to_check in tracks:

            for cache_track in return_tracks:
                if to_check.name.lower() == cache_track.name.lower():
                    if to_check.artists[0].name.lower() == cache_track.artists[0].name.lower():
                        break
            else:
                return_tracks.append(to_check)

        return return_tracks
