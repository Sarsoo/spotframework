from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union
from spotframework.model.uri import Uri
import spotframework.model.artist
import spotframework.model.service
import spotframework.model.track


@dataclass
class SimplifiedAlbum:
    class Type(Enum):
        single = 0
        compilation = 1
        album = 2

    album_type: SimplifiedAlbum.Type
    artists: List[spotframework.model.artist.SimplifiedArtist]
    available_markets: List[str]
    external_urls: dict
    href: str
    id: str
    images: List[spotframework.model.service.Image]
    name: str
    release_date: datetime
    release_date_precision: str
    type: str
    uri: Union[str, Uri]
    total_tracks: int = None

    def __post_init__(self):

        if isinstance(self.album_type, str):
            self.album_type = SimplifiedAlbum.Type[self.album_type.strip().lower()]

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.album:
                raise TypeError('provided uri not for an album')

        if all((isinstance(i, dict) for i in self.artists)):
            self.artists = [spotframework.model.artist.SimplifiedArtist(**i) for i in self.artists]

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [spotframework.model.service.Image(**i) for i in self.images]

        if isinstance(self.release_date, str):
            if self.release_date_precision == 'year':
                self.release_date = datetime.strptime(self.release_date, '%Y')
            elif self.release_date_precision == 'month':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m')
            elif self.release_date_precision == 'day':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m-%d')

    @property
    def artists_names(self) -> str:
        return self._join_strings([i.name for i in self.artists])

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ', '.join(string_list)

    def __str__(self):
        artists = ', '.join([i.name for i in self.artists]) if self.artists is not None else 'n/a'

        return f'{self.name} / {artists}'


@dataclass
class AlbumFull(SimplifiedAlbum):

    copyrights: List[dict] = None
    external_ids: dict = None
    genres: List[str] = None

    label: str = None
    popularity: int = None
    tracks: List[spotframework.model.track.SimplifiedTrack] = None

    def __post_init__(self):

        if isinstance(self.album_type, str):
            self.album_type = SimplifiedAlbum.Type[self.album_type]

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.album:
                raise TypeError('provided uri not for an album')

        if all((isinstance(i, dict) for i in self.artists)):
            self.artists = [spotframework.model.artist.SimplifiedArtist(**i) for i in self.artists]

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [spotframework.model.service.Image(**i) for i in self.images]

        if all((isinstance(i, dict) for i in self.tracks)):
            self.tracks = [spotframework.model.track.SimplifiedTrack(**i) for i in self.tracks]

        if isinstance(self.release_date, str):
            if self.release_date_precision == 'year':
                self.release_date = datetime.strptime(self.release_date, '%Y')
            elif self.release_date_precision == 'month':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m')
            elif self.release_date_precision == 'day':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m-%d')


@dataclass
class LibraryAlbum:
    added_at: datetime
    album: AlbumFull

    def __post_init__(self):
        if isinstance(self.album, dict):
            self.album = AlbumFull(**self.album)

        if isinstance(self.added_at, str):
            self.added_at = datetime.strptime(self.added_at, '%Y-%m-%dT%H:%M:%S%z')
