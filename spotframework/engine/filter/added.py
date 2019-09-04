from abc import ABC, abstractmethod
from .abstract import AbstractProcessor
import datetime
from typing import List
from spotframework.model.track import Track, PlaylistTrack


class Added(AbstractProcessor, ABC):

    def __init__(self,
                 boundary: datetime.datetime,
                 names: List[str] = None,
                 keep_malformed_type: bool = True):
        super().__init__(names)
        self.boundary = boundary
        self.keep_malformed_type = keep_malformed_type

    @abstractmethod
    def check_date(self, track: PlaylistTrack):
        pass

    def process(self, tracks: List[Track]):

        return_tracks = []
        malformed_tracks = []

        for track in tracks:
            if isinstance(track, PlaylistTrack):
                if self.check_date(track):
                    return_tracks.append(track)
            else:
                malformed_tracks.append(track)

        if self.keep_malformed_type:
            return_tracks += malformed_tracks

        return return_tracks


class AddedBefore(Added):
    def check_date(self, track: PlaylistTrack):
        return track.added_at < self.boundary


class AddedSince(Added):
    def check_date(self, track: PlaylistTrack):
        return track.added_at > self.boundary
