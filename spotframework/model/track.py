from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List
from datetime import datetime
if TYPE_CHECKING:
    from spotframework.model.album import Album
    from spotframework.model.artist import Artist
    from spotframework.model.user import User


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
    def artists_names(self):
        return self._join_strings([i.name for i in self.artists])

    @property
    def album_artists_names(self):
        return self.album.artists_names

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ' , '.join(string_list)

    def __str__(self):
        album = self.album.name if self.album else 'n/a'
        artists = ' , '.join([i.name for i in self.artists]) if self.artists else 'n/a'

        return f'{self.name} / {album} / {artists}'


class SpotifyTrack(Track):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 href: str = None,
                 spotify_id: str = None,
                 uri: str = None,

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
        self.spotify_id = spotify_id
        self.uri = uri
        self.is_playable = is_playable

        self.popularity = popularity


class PlaylistTrack(SpotifyTrack):
    def __init__(self,
                 name: str,
                 album: Album,
                 artists: List[Artist],

                 added_at: str,
                 added_by: User,
                 is_local: bool,

                 href: str = None,
                 spotify_id: str = None,
                 uri: str = None,

                 disc_number: int = None,
                 duration_ms: int = None,
                 explicit: bool = None,
                 is_playable: bool = None,

                 popularity: int = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         spotify_id=spotify_id,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity)

        self.added_at = datetime.fromisoformat(added_at.replace('T', ' ').replace('Z', ''))
        self.added_by = added_by
        self.is_local = is_local
