from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union
import logging
from spotframework.model.uri import Uri
import spotframework.model.artist
import spotframework.model.service
import spotframework.model.track

from spotframework.model import init_with_key_filter

logger = logging.getLogger(__name__)

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
            if self.uri.object_type not in [Uri.ObjectType.album, Uri.ObjectType.show]:
                raise TypeError('provided uri not for an album')

        if all((isinstance(i, dict) for i in self.artists)):
            self.artists = [init_with_key_filter(spotframework.model.artist.SimplifiedArtist, i) for i in self.artists]

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [init_with_key_filter(spotframework.model.service.Image, i) for i in self.images]

        if isinstance(self.release_date, str):
            if self.release_date_precision == 'year':
                self.release_date = datetime.strptime(self.release_date, '%Y')
            elif self.release_date_precision == 'month':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m')
            elif self.release_date_precision == 'day':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m-%d')
            else:
                logger.error(f'invalid release date type {self.release_date_precision} - {self.release_date}')

        elif self.release_date is None and self.release_date_precision is None: # for podcasts
            self.release_date = datetime(year=1900, month=1, day=1)

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
        super().__post_init__()

        if all((isinstance(i, dict) for i in self.tracks)):
            self.tracks = [init_with_key_filter(spotframework.model.track.SimplifiedTrack, i) for i in self.tracks]


@dataclass
class LibraryAlbum:
    added_at: datetime
    album: AlbumFull

    def __post_init__(self):
        if isinstance(self.album, dict):
            self.album = init_with_key_filter(AlbumFull, self.album)

        if isinstance(self.added_at, str):
            self.added_at = datetime.strptime(self.added_at, '%Y-%m-%dT%H:%M:%S%z')
