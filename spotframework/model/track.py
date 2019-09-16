from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List, Union
from datetime import datetime
from spotframework.model.uri import Uri
from spotframework.util.console import Color
if TYPE_CHECKING:
    from spotframework.model.album import Album
    from spotframework.model.artist import Artist
    from spotframework.model.user import User
    from spotframework.model.service import Context


class Track:
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 disc_number: int = None,
                 duration_ms: int = None,
                 excplicit: bool = None
                 ):
        self.name = name
        self.album = album
        self.artists = artists

        self.disc_number = disc_number
        self.duration_ms = duration_ms
        self.explicit = excplicit

    @property
    def artists_names(self) -> str:
        return self._join_strings([i.name for i in self.artists])

    @property
    def album_artists_names(self) -> str:
        return self.album.artists_names

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ', '.join(string_list)

    def __str__(self):
        album = self.album.name if self.album else 'n/a'
        artists = ', '.join([i.name for i in self.artists]) if self.artists else 'n/a'

        return f'{self.name} / {album} / {artists}'

    def __repr__(self):
        return Color.YELLOW + Color.BOLD + 'Track' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}'


class SpotifyTrack(Track):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 disc_number: int = None,
                 duration_ms: int = None,
                 explicit: bool = None,
                 is_playable: bool = None,

                 popularity: int = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         excplicit=explicit)

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri
        self.is_playable = is_playable

        self.popularity = popularity

    def __repr__(self):
        return Color.BOLD + Color.YELLOW + 'SpotifyTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}'


class LibraryTrack(SpotifyTrack):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 disc_number: int = None,
                 duration_ms: int = None,
                 explicit: bool = None,
                 is_playable: bool = None,

                 popularity: int = None,

                 added_at: datetime = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity)

        self.added_at = added_at

    def __repr__(self):
        return Color.BOLD + Color.YELLOW + 'LibraryTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.added_at}'


class PlaylistTrack(SpotifyTrack):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 added_at: datetime,
                 added_by: User,
                 is_local: bool,

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 disc_number: int = None,
                 duration_ms: int = None,
                 explicit: bool = None,
                 is_playable: bool = None,

                 popularity: int = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity)

        self.added_at = added_at
        self.added_by = added_by
        self.is_local = is_local

    def __repr__(self):
        return Color.BOLD + Color.YELLOW + 'PlaylistTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.added_at}'


class PlayedTrack(SpotifyTrack):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 disc_number: int = None,
                 duration_ms: int = None,
                 explicit: bool = None,
                 is_playable: bool = None,

                 popularity: int = None,

                 played_at: datetime = None,
                 context: Context = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity)
        self.played_at = played_at
        self.context = context

    def __repr__(self):
        return Color.BOLD + Color.YELLOW + 'PlayedTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.played_at}'
