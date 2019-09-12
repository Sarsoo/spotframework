from abc import ABC
from .abstract import AbstractProcessor, BatchSingleTypeAwareProcessor
from typing import List
from spotframework.model.track import Track, PlaylistTrack


class BasicReversibleSort(AbstractProcessor, ABC):
    def __init__(self,
                 names: List[str] = None,
                 reverse: bool = False):
        super().__init__(names)
        self.reverse = reverse


class SortReleaseDate(BasicReversibleSort):

    def process(self, tracks: List[Track]) -> List[Track]:
        tracks.sort(key=lambda x: x.album.release_date, reverse=self.reverse)
        return tracks


class SortArtistName(BasicReversibleSort):

    def process(self, tracks: List[Track]) -> List[Track]:
        tracks.sort(key=lambda x: x.artists[0].name, reverse=self.reverse)
        return tracks


class SortAddedDate(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 reverse: bool = False,
                 append_malformed: bool = True):
        super().__init__(names=names,
                         instance_check=PlaylistTrack,
                         append_malformed=append_malformed)
        self.reverse = reverse

    def process_batch(self, tracks: List[PlaylistTrack]) -> List[PlaylistTrack]:
        tracks.sort(key=lambda x: x.added_at, reverse=self.reverse)
        return tracks
