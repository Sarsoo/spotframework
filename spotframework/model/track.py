from __future__ import annotations
from typing import TYPE_CHECKING
from typing import List, Union
from datetime import datetime
from spotframework.model.uri import Uri
from spotframework.util.console import Color
from spotframework.util import convert_ms_to_minute_string
from enum import Enum
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
        album = self.album.name if self.album is not None else 'n/a'
        artists = ', '.join([i.name for i in self.artists]) if self.artists is not None else 'n/a'

        return f'{self.name} / {album} / {artists}'

    def __repr__(self):
        return Color.YELLOW + Color.BOLD + 'Track' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}'

    def __eq__(self, other):
        return isinstance(other, Track) and other.name == self.name and other.artists == self.artists

    @staticmethod
    def wrap(name: str = None,
             artists: List[str] = None,
             album: str = None,
             album_artists: List[str] = None):
        return Track(name=name,
                     album=Album.wrap(name=album, artists=album_artists),
                     artists=[Artist(i) for i in artists])


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

                 popularity: int = None,

                 audio_features: AudioFeatures = None
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

        if self.uri.object_type != Uri.ObjectType.track:
            raise TypeError('provided uri not for a track')

        self.is_playable = is_playable

        self.popularity = popularity

        self.audio_features = audio_features

    def __repr__(self):
        string = Color.BOLD + Color.YELLOW + 'SpotifyTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}'

        if self.audio_features is not None:
            string += ' ' + repr(self.audio_features)

        return string

    def __eq__(self, other):
        return isinstance(other, SpotifyTrack) and other.uri == self.uri

    @staticmethod
    def wrap(uri: Uri = None,
             name: str = None,
             artists: Union[str, List[str]] = None,
             album: str = None,
             album_artists: Union[str, List[str]] = None):
        if uri:
            return SpotifyTrack(name=None, album=None, artists=None, uri=uri)
        else:
            return super().wrap(name=name, artists=artists, album=album, album_artists=album_artists)


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

                 audio_features: AudioFeatures = None,

                 added_at: datetime = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity,
                         audio_features=audio_features)

        self.added_at = added_at

    def __repr__(self):
        string = Color.BOLD + Color.YELLOW + 'LibraryTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.added_at}'

        if self.audio_features is not None:
            string += ' ' + repr(self.audio_features)

        return string


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

                 popularity: int = None,

                 audio_features: AudioFeatures = None
                 ):
        super().__init__(name=name, album=album, artists=artists,
                         href=href,
                         uri=uri,

                         disc_number=disc_number,
                         duration_ms=duration_ms,
                         explicit=explicit,
                         is_playable=is_playable,
                         popularity=popularity,
                         audio_features=audio_features)

        self.added_at = added_at
        self.added_by = added_by
        self.is_local = is_local

    def __repr__(self):
        string = Color.BOLD + Color.YELLOW + 'PlaylistTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.added_at}'

        if self.audio_features is not None:
            string += ' ' + repr(self.audio_features)

        return string


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

                 audio_features: AudioFeatures = None,

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
                         popularity=popularity,
                         audio_features=audio_features)
        self.played_at = played_at
        self.context = context

    def __repr__(self):
        string = Color.BOLD + Color.YELLOW + 'PlayedTrack' + Color.END + \
               f': {self.name}, ({self.album}), {self.artists}, {self.uri}, {self.played_at}'

        if self.audio_features is not None:
            string += ' ' + repr(self.audio_features)

        return string


class AudioFeatures:

    class Mode(Enum):
        MINOR = 0
        MAJOR = 1

    def __init__(self,
                 acousticness: float,
                 analysis_url: str,
                 danceability: float,
                 duration_ms: int,
                 energy: float,
                 uri: Uri,
                 instrumentalness: float,
                 key: int,
                 liveness: float,
                 loudness: float,
                 mode: int,
                 speechiness: float,
                 tempo: float,
                 time_signature: int,
                 track_href: str,
                 valence: float):
        self.acousticness = self.check_float(acousticness)
        self.analysis_url = analysis_url
        self.danceability = self.check_float(danceability)
        self.duration_ms = duration_ms
        self.energy = self.check_float(energy)
        self.uri = uri
        self.instrumentalness = self.check_float(instrumentalness)
        self._key = key
        self.liveness = self.check_float(liveness)
        self.loudness = loudness

        if mode == 0:
            self.mode = self.Mode.MINOR
        elif mode == 1:
            self.mode = self.Mode.MAJOR
        else:
            raise ValueError('illegal value for mode')
        self.speechiness = self.check_float(speechiness)
        self.tempo = tempo
        self.time_signature = time_signature
        self.track_href = track_href
        self.valence = self.check_float(valence)

    def to_dict(self):
        return {
            'acousticness': self.acousticness,
            'analysis_url': self.analysis_url,
            'danceability': self.danceability,
            'duration_ms': self.duration_ms,
            'energy': self.energy,
            'uri': str(self.uri) if self.uri is not None else None,
            'instrumentalness': self.instrumentalness,
            'key': self.key,
            'key_code': self._key,
            'liveness': self.liveness,
            'loudness': self.loudness,
            'mode': self.mode.value,
            'speechiness': self.speechiness,
            'tempo': self.tempo,
            'time_signature': self.time_signature,
            'track_href': self.track_href,
            'valence': self.valence
        }

    @property
    def key(self) -> str:
        legend = {
            0: 'C',
            1: 'C#',
            2: 'D',
            3: 'D#',
            4: 'E',
            5: 'F',
            6: 'F#',
            7: 'G',
            8: 'G#',
            9: 'A',
            10: 'A#',
            11: 'B'
        }
        if legend.get(self._key, None):
            return legend.get(self._key, None)
        else:
            raise ValueError('key value out of bounds')

    @key.setter
    def key(self, value):
        if isinstance(value, int):
            if 0 <= value <= 11:
                self._key = value
            else:
                raise ValueError('key value out of bounds')
        else:
            raise ValueError('key value not integer')

    def is_live(self):
        if self.liveness is not None:
            if self.liveness > 0.8:
                return True
            else:
                return False
        else:
            raise ValueError('no value for liveness')

    def is_instrumental(self):
        if self.instrumentalness is not None:
            if self.instrumentalness > 0.5:
                return True
            else:
                return False
        else:
            raise ValueError('no value for instrumentalness')

    def is_spoken_word(self):
        if self.speechiness is not None:
            if self.speechiness > 0.66:
                return True
            else:
                return False
        else:
            raise ValueError('no value for speechiness')

    @staticmethod
    def check_float(value):
        value = float(value)

        if isinstance(value, float):
            if 0 <= value <= 1:
                return value
            else:
                raise ValueError(f'value {value} out of bounds')
        else:
            raise ValueError(f'value {value} is not float')

    def __repr__(self):
        return Color.BOLD + Color.DARKCYAN + 'AudioFeatures' + Color.END + \
               f': acoustic:{self.acousticness}, dance:{self.danceability}, ' \
                   f'duration:{convert_ms_to_minute_string(self.duration_ms)}, energy:{self.energy}, ' \
                   f'instrumental:{self.instrumentalness}, key:{self.key}, live:{self.liveness}, ' \
                   f'volume:{self.loudness}db, mode:{self.mode.name}, speech:{self.speechiness}, tempo:{self.tempo}, ' \
                   f'time_sig:{self.time_signature}, valence:{self.valence}'
