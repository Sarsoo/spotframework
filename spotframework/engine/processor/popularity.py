from spotframework.engine.processor.abstract import BatchSingleTypeAwareProcessor
from typing import List
from spotframework.model.track import TrackFull
from spotframework.model.uri import Uri


class SortPopularity(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 append_malformed: bool = True,
                 reverse: bool = False):
        super().__init__(names=names,
                         uris=uris,
                         instance_check=TrackFull,
                         append_malformed=append_malformed)
        self.reverse = reverse

    def process_batch(self, tracks: List[TrackFull]) -> List[TrackFull]:
        tracks.sort(key=lambda x: x.popularity, reverse=self.reverse)
        return tracks
