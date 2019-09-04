from .abstract import AbstractProcessor
from typing import List
from spotframework.model.track import Track


class SortReverseReleaseDate(AbstractProcessor):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.album.release_date, reverse=True)
        return tracks


class SortReleaseDate(AbstractProcessor):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.album.release_date, reverse=False)
        return tracks


class SortArtistName(AbstractProcessor):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.artists[0].name, reverse=False)
        return tracks


class SortReverseArtistName(AbstractProcessor):

    def process(self, tracks: List[Track]):
        tracks.sort(key=lambda x: x.artists[0].name, reverse=True)
        return tracks
