from spotframework.engine.filter.abstract import AbstractProcessor
from typing import List
from spotframework.model.track import Track, SpotifyTrack


class SortPopularity(AbstractProcessor):

    def __init__(self,
                 names: List[str] = None,
                 keep_malformed_type: bool = True):
        super().__init__(names)
        self.keep_malformed_type = keep_malformed_type

    def sort(self, tracks: List[SpotifyTrack]):
        tracks.sort(key=lambda x: x.popularity, reverse=True)

    def process(self, tracks: List[Track]):
        return_tracks = []
        malformed_tracks = []

        for track in tracks:
            if isinstance(track, SpotifyTrack):
                return_tracks.append(track)
            else:
                malformed_tracks.append(track)

        self.sort(return_tracks)

        if self.keep_malformed_type:
            return_tracks += malformed_tracks

        return return_tracks


class SortReversePopularity(SortPopularity):

    def sort(self, tracks: List[SpotifyTrack]):
        tracks.sort(key=lambda x: x.popularity, reverse=False)
