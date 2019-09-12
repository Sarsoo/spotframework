from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List
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
        return ' , '.join(string_list)

    def __str__(self):
        artists = ' , '.join([i.name for i in self.artists]) if self.artists else 'n/a'

        return f'{self.name} / {artists}'


class SpotifyAlbum(Album):
    def __init__(self,
                 name: str,
                 artists: List[Artist],

                 href: str = None,
                 spotify_id: str = None,
                 uri: str = None,

                 genres: List[str] = None,
                 tracks: List = None,

                 release_date: str = None,
                 release_date_precision: str = None,

                 label: str = None,
                 popularity: int = None
                 ):
        super().__init__(name, artists)

        self.href = href
        self.spotify_id = spotify_id
        self.uri = uri

        self.genres = genres
        self.tracks = tracks

        self.release_date = release_date
        self.release_date_precision = release_date_precision

        self.label = label
        self.popularity = popularity
