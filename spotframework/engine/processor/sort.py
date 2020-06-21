from abc import ABC
from .abstract import AbstractProcessor, BatchSingleTypeAwareProcessor
from typing import List
from spotframework.model.track import SimplifiedTrack, PlaylistTrack
from spotframework.model.uri import Uri


class BasicReversibleSort(AbstractProcessor, ABC):
    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 reverse: bool = False):
        super().__init__(names=names, uris=uris)
        self.reverse = reverse


class SortReleaseDate(BasicReversibleSort):

    def process(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:
        tracks.sort(key=lambda x: (x.artists[0].name.lower(),
                                   x.album.name.lower(),
                                   x.track_number))
        tracks.sort(key=lambda x: x.album.release_date, reverse=self.reverse)
        return tracks


class SortArtistName(BasicReversibleSort):

    def process(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:
        tracks.sort(key=lambda x: (x.album.name.lower(),
                                   x.track_number))
        tracks.sort(key=lambda x: x.artists[0].name.lower(), reverse=self.reverse)
        return tracks


class SortAddedDate(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 reverse: bool = False,
                 append_malformed: bool = True):
        super().__init__(names=names,
                         uris=uris,
                         instance_check=PlaylistTrack,
                         append_malformed=append_malformed)
        self.reverse = reverse

    def process_batch(self, tracks: List[PlaylistTrack]) -> List[PlaylistTrack]:
        tracks.sort(key=lambda x: (x.artists[0].name.lower(),
                                   x.album.name.lower(),
                                   x.track_number))
        tracks.sort(key=lambda x: x.added_at, reverse=self.reverse)
        return tracks
