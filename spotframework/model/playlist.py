from spotframework.model.user import User
from spotframework.model.track import Track, SpotifyTrack, PlaylistTrack
from spotframework.model.uri import Uri
from spotframework.util.console import Color
from tabulate import tabulate
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class Playlist:

    def __init__(self,
                 name: str = None,
                 description: str = None):
        self._tracks = []
        self.name = name
        self.description = description

    def has_tracks(self) -> bool:
        if len(self.tracks) > 0:
            return True
        else:
            return False

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, item) -> Track:
        return self.tracks[item]

    def __iter__(self):
        return iter(self.tracks)

    @property
    def tracks(self) -> List[Track]:
        return self._tracks

    @tracks.setter
    def tracks(self, value: List[Track]):
        tracks = []
        not_tracks = []

        for track in value:
            if isinstance(track, Track):
                tracks.append(track)
            else:
                not_tracks.append(track)

        if len(not_tracks) > 0:
            logger.error('playlist tracks must be off type Track')

        self._tracks = tracks

    def __str__(self):

        prefix = f'\n==={self.name}===\n\n' if self.name is not None else ''

        table = prefix + self.get_tracks_string() + '\n' + f'total: {len(self)}'
        return table

    def __repr__(self):
        return Color.GREEN + Color.BOLD + 'Playlist' + Color.END + \
               f': {self.name}, ({len(self)})'

    def __add__(self, other):
        if isinstance(other, Track):
            self.tracks.append(other)
            return self

        elif isinstance(other, list):
            if all((isinstance(i, Track) for i in other)):
                self.tracks += other
                return self
            else:
                logger.error('list not full of tracks')
                raise TypeError('list not full of tracks')

        else:
            logger.error('list of tracks needed to add')
            raise TypeError('list of tracks needed to add')

    def __sub__(self, other):
        if isinstance(other, Track):
            self.tracks.remove(other)
            return self

        elif isinstance(other, list):
            if all((isinstance(i, Track) for i in other)):
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
            track_row = [track.name,
                         track.album.name,
                         track.artists_names,
                         track.added_at if isinstance(track, PlaylistTrack) else '',
                         track.popularity if isinstance(track, SpotifyTrack) else '',
                         track.uri if isinstance(track, SpotifyTrack) else '']

            rows.append(track_row)

        table = tabulate(rows, headers=headers, showindex='always', tablefmt="fancy_grid")

        return table


class SpotifyPlaylist(Playlist):

    def __init__(self,
                 uri: Union[str, Uri],

                 name: str = None,
                 owner: User = None,
                 description: str = None,

                 href: str = None,

                 collaborative: bool = None,
                 public: bool = None,
                 ext_spotify: str = None):

        super().__init__(name=name, description=description)

        self.owner = owner

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri

        if self.uri.object_type != Uri.ObjectType.playlist:
            raise TypeError('provided uri not for a playlist')

        self.collaborative = collaborative
        self.public = public
        self.ext_spotify = ext_spotify

    def __str__(self):

        prefix = f'\n==={self.name}===\n\n' if self.name is not None else ''
        prefix += f'uri: {self.uri}\n' if self.uri is not None else ''

        table = prefix + self.get_tracks_string() + '\n' + f'total: {len(self)}'

        return table

    def __repr__(self):
        return Color.GREEN + Color.BOLD + 'SpotifyPlaylist' + Color.END + \
               f': {self.name} ({self.owner}), ({len(self)}), {self.uri}'
