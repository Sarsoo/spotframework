from abc import ABC
from .abstract import AbstractProcessor
from typing import List
from spotframework.model.track import Track


class BasicReversibleSort(AbstractProcessor, ABC):
    def __init__(self,
                 names: List[str] = None,
                 reverse: bool = False):
        super().__init__(names)
        self.reverse = reverse


class SortReleaseDate(BasicReversibleSort):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.album.release_date, reverse=self.reverse)
        return tracks


class SortArtistName(BasicReversibleSort):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.artists[0].name, reverse=self.reverse)
        return tracks
