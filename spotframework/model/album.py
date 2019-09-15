from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List, Union
from spotframework.util.console import Color
from spotframework.model.uri import Uri
if TYPE_CHECKING:
    from spotframework.model.artist import Artist


class Album:
    def __init__(self, name: str, artists: List[Artist]):
        self.name = name
        self.artists = artists

    @property
    def artists_names(self) -> str:
        return self._join_strings([i.name for i in self.artists])

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ', '.join(string_list)

    def __str__(self):
        artists = ', '.join([i.name for i in self.artists]) if self.artists else 'n/a'

        return f'{self.name} / {artists}'

    def __repr__(self):
        return Color.DARKCYAN + Color.BOLD + 'Album' + Color.END + \
               f': {self.name}, [{self.artists}]'


class SpotifyAlbum(Album):
    def __init__(self,
                 name: str,
                 artists: List[Artist],

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 genres: List[str] = None,
                 tracks: List = None,

                 release_date: str = None,
                 release_date_precision: str = None,

                 label: str = None,
                 popularity: int = None
                 ):
        super().__init__(name, artists)

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri

        self.genres = genres
        self.tracks = tracks

        self.release_date = release_date
        self.release_date_precision = release_date_precision

        self.label = label
        self.popularity = popularity

    def __repr__(self):
        return Color.DARKCYAN + Color.BOLD + 'SpotifyAlbum' + Color.END + \
               f': {self.name}, {self.artists}, {self.uri}, {self.tracks}'
