from .abstract import BatchSingleTypeAwareProcessor
import datetime
from typing import List
from spotframework.model.track import PlaylistTrack, LibraryTrack
from spotframework.model.uri import Uri
from typing import Optional


class Added(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 boundary: datetime.datetime,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 append_malformed: bool = True):
        super().__init__(names=names,
                         uris=uris,
                         instance_check=[PlaylistTrack, LibraryTrack],
                         append_malformed=append_malformed)
        self.boundary = boundary


class AddedBefore(Added):
    def process_single(self, track: PlaylistTrack) -> Optional[PlaylistTrack]:
        if track.added_at < self.boundary:
            return track


class AddedSince(Added):
    def process_single(self, track: PlaylistTrack) -> Optional[PlaylistTrack]:
        if track.added_at > self.boundary:
            return track
