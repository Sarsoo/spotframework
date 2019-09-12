from spotframework.engine.processor.abstract import BatchSingleProcessor, BatchSingleTypeAwareProcessor
from typing import List
from spotframework.model.track import Track, SpotifyTrack


class DeduplicateByID(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 append_malformed: bool = True):
        super().__init__(names,
                         instance_check=SpotifyTrack,
                         append_malformed=append_malformed)

    def process_batch(self, tracks: List[SpotifyTrack]) -> List[SpotifyTrack]:
        return_tracks = []

        for track in tracks:
            if track.uri not in [i.uri for i in return_tracks]:
                return_tracks.append(track)

        return return_tracks


class DeduplicateByName(BatchSingleProcessor):

    def process_batch(self, tracks: List[Track]) -> List[Track]:
        return_tracks = []

        for to_check in tracks:

            for cache_track in return_tracks:
                if to_check.name.lower() == cache_track.name.lower():
                    if to_check.artists[0].name.lower() == cache_track.artists[0].name.lower():
                        break
            else:
                return_tracks.append(to_check)

        return return_tracks
