from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from typing import List, Union
from spotframework.util.console import Color
from spotframework.model.uri import Uri
if TYPE_CHECKING:
    from spotframework.model.artist import Artist
    from spotframework.model.track import Track


class Album:
    def __init__(self, name: str, artists: List[Artist], tracks: List[Track] = None):
        self.name = name
        self.artists = artists
        if tracks is not None:
            self.tracks = tracks
        else:
            self.tracks = []

    @property
    def artists_names(self) -> str:
        return self._join_strings([i.name for i in self.artists])

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ', '.join(string_list)

    def __str__(self):
        artists = ', '.join([i.name for i in self.artists]) if self.artists is not None else 'n/a'

        return f'{self.name} / {artists}'

    def __repr__(self):
        return Color.DARKCYAN + Color.BOLD + 'Album' + Color.END + \
               f': {self.name}, [{self.artists}]'

    def __len__(self):
        return len(self.tracks)

    @staticmethod
    def wrap(name: str = None,
             artists: Union[str, List[str]] = None):
        return Album(name=name, artists=[Artist(i) for i in artists])


class SpotifyAlbum(Album):

    class Type(Enum):
        single = 0
        compilation = 1
        album = 2

    def __init__(self,
                 name: str,
                 artists: List[Artist],
                 album_type: Type,

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 genres: List[str] = None,
                 tracks: List[Track] = None,

                 release_date: str = None,
                 release_date_precision: str = None,

                 label: str = None,
                 popularity: int = None
                 ):
        super().__init__(name, artists, tracks=tracks)

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.album:
                raise TypeError('provided uri not for an album')

        self.album_type = album_type

        self.genres = genres

        self.release_date = release_date
        self.release_date_precision = release_date_precision

        self.label = label
        self.popularity = popularity

    def __repr__(self):
        return Color.DARKCYAN + Color.BOLD + 'SpotifyAlbum' + Color.END + \
               f': {self.name}, {self.artists}, {self.uri}, {self.tracks}'

    @staticmethod
    def wrap(uri: Uri = None,
             name: str = None,
             artists: Union[str, List[str]] = None):

        if uri:
            return SpotifyAlbum(name=None, artists=None, uri=uri)
        else:
            return super().wrap(name=name, artists=artists)


class LibraryAlbum(SpotifyAlbum):
    def __init__(self,
                 name: str,
                 artists: List[Artist],

                 album_type: SpotifyAlbum.Type,

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 genres: List[str] = None,
                 tracks: List = None,

                 release_date: str = None,
                 release_date_precision: str = None,

                 label: str = None,
                 popularity: int = None,

                 added_at: datetime = None
                 ):
        super().__init__(name=name,
                         artists=artists,
                         album_type=album_type,
                         href=href,
                         uri=uri,
                         genres=genres,
                         tracks=tracks,
                         release_date=release_date,
                         release_date_precision=release_date_precision,
                         label=label,
                         popularity=popularity)
        self.added_at = added_at
