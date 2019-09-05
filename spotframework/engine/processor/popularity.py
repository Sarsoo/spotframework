from spotframework.engine.processor.abstract import BatchSingleTypeAwareProcessor
from typing import List
from spotframework.model.track import SpotifyTrack


class SortPopularity(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 append_malformed: bool = True,
                 reverse: bool = False):
        super().__init__(names,
                         instance_check=SpotifyTrack,
                         append_malformed=append_malformed)
        self.reverse = reverse

    def process_batch(self, tracks: List[SpotifyTrack]):
        tracks.sort(key=lambda x: x.popularity, reverse=self.reverse)
        return tracks
