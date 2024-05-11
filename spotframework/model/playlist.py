from dataclasses import dataclass
from spotframework.model.user import PublicUser
from spotframework.model.track import TrackFull, PlaylistTrack
from spotframework.model.uri import Uri
from spotframework.model.service import Image
from spotframework.model import init_with_key_filter
from tabulate import tabulate
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimplifiedPlaylist:
    collaborative: bool
    description: str
    external_urls: dict
    href: str
    id: str
    images: List[Image]
    name: str
    owner: PublicUser
    primary_color: str
    public: bool
    snapshot_id: str
    tracks: List[PlaylistTrack]
    type: str
    uri: Union[str, Uri]

    def __post_init__(self):
        if isinstance(self.tracks, dict):
            self.tracks = []

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.playlist:
                raise TypeError('provided uri not for a playlist')

        if (images := getattr(self, "images")) and all((isinstance(i, dict) for i in images)):
            self.images = [init_with_key_filter(Image, i) for i in self.images]

        if isinstance(self.owner, dict):
            self.owner = init_with_key_filter(PublicUser, self.owner)

    def has_tracks(self) -> bool:
        return bool(len(self.tracks) > 0)

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, item) -> PlaylistTrack:
        return self.tracks[item]

    def __iter__(self):
        return iter(self.tracks)

    def __str__(self):
        prefix = f'\n==={self.name}===\n\n' if self.name is not None else ''

        table = prefix + self.get_tracks_string() + '\n' + f'total: {len(self)}'
        return table

    def __add__(self, other):
        if isinstance(other, PlaylistTrack):
            self.tracks.append(other)
            return self

        elif isinstance(other, list):
            if all((isinstance(i, PlaylistTrack) for i in other)):
                self.tracks += other
                return self
            else:
                logger.error('list not full of tracks')
                raise TypeError('list not full of tracks')

        else:
            logger.error('list of tracks needed to add')
            raise TypeError('list of tracks needed to add')

    def __sub__(self, other):
        if isinstance(other, PlaylistTrack):
            self.tracks.remove(other)
            return self

        elif isinstance(other, list):
            if all((isinstance(i, PlaylistTrack) for i in other)):
                self.tracks -= other
                return self
            else:
                logger.error('list not full of tracks')
                raise TypeError('list not full of tracks')

        else:
            logger.error('list of tracks needed to subtract')
            raise TypeError('list of tracks needed to subtract')

    def get_tracks_string(self):

        rows = []
        headers = ['name', 'album', 'artist', 'added at', 'popularity', 'uri']
        for track in self.tracks:
            track_row = [track.track.name,
                         track.track.album.name,
                         track.track.artists_names,
                         track.added_at if isinstance(track, PlaylistTrack) else '',
                         track.popularity if isinstance(track, TrackFull) else '',
                         track.uri if isinstance(track, TrackFull) else '']

            rows.append(track_row)

        table = tabulate(rows, headers=headers, showindex='always', tablefmt="fancy_grid")

        return table


@dataclass
class FullPlaylist(SimplifiedPlaylist):
    followers: dict = None

    def __post_init__(self):
        if isinstance(self.tracks, dict):
            self.tracks = []

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.playlist:
                raise TypeError('provided uri not for a playlist')

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [init_with_key_filter(Image, i) for i in self.images]

        if isinstance(self.owner, dict):
            self.owner = init_with_key_filter(PublicUser, self.owner)

    def __str__(self):
        prefix = f'\n==={self.name}===\n\n' if self.name is not None else ''
        prefix += f'uri: {self.uri}\n' if self.uri is not None else ''

        table = prefix + self.get_tracks_string() + '\n' + f'total: {len(self)}'

        return table
