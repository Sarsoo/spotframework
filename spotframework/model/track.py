from __future__ import annotations
from typing import Union, List
from datetime import datetime
from dataclasses import dataclass, field
import logging

import spotframework.model
from spotframework.model.uri import Uri
from enum import Enum
import spotframework.model.album
import spotframework.model.artist
import spotframework.model.service
import spotframework.model.user
from spotframework.model.podcast import EpisodeFull

from spotframework.model import init_with_key_filter

logger = logging.getLogger(__name__)


@dataclass
class SimplifiedTrack:
    artists: List[spotframework.model.artist.SimplifiedArtist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    external_urls: dict
    explicit: bool
    href: str
    id: str
    name: str
    preview_url: str
    track_number: int
    type: str
    uri: Union[str, Uri]
    is_local: bool
    is_playable: bool = None
    episode: bool = None
    track: bool = None

    def __post_init__(self):
        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type not in [Uri.ObjectType.track, Uri.ObjectType.episode]:
                raise TypeError('provided uri not for a track')

        if all((isinstance(i, dict) for i in self.artists)):
            self.artists = [init_with_key_filter(spotframework.model.artist.SimplifiedArtist, i) for i in self.artists]

    @property
    def artists_names(self) -> str:
        return self._join_strings([i.name for i in self.artists])

    @staticmethod
    def _join_strings(string_list: List[str]):
        return ', '.join(string_list)

    def __str__(self):
        artists = ', '.join([i.name for i in self.artists]) if self.artists is not None else 'n/a'

        return f'{self.name} / {artists}'

    def __eq__(self, other):
        return isinstance(other, SimplifiedTrack) and other.name == self.name and other.artists == self.artists


@dataclass
class TrackFull(SimplifiedTrack):
    album: spotframework.model.album.SimplifiedAlbum = None
    external_ids: dict = None
    popularity: int = None

    @property
    def album_artists_names(self) -> str:
        return self.album.artists_names

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.album, dict):
            self.album = init_with_key_filter(spotframework.model.album.SimplifiedAlbum, self.album)

    def __eq__(self, other):
        return isinstance(other, TrackFull) and other.uri == self.uri


@dataclass
class LibraryTrack:
    added_at: datetime
    track: TrackFull

    def __post_init__(self):
        if isinstance(self.track, dict):
            self.track = init_with_key_filter(TrackFull, self.track)

        if isinstance(self.added_at, str):
            self.added_at = datetime.strptime(self.added_at, '%Y-%m-%dT%H:%M:%S%z')


@dataclass
class PlaylistTrack:
    added_at: datetime
    added_by: spotframework.model.user.PublicUser
    is_local: bool
    primary_color: str
    track: Union[TrackFull, EpisodeFull]
    video_thumbnail: dict

    def __post_init__(self):
        if isinstance(self.track, dict):

            # below seems more intuitive, currently parsing episode to track/album/artist structure for
            # serialising over api, below could be implemented

            # obj_type = None
            # if self.track['type'] == 'track':
            #     obj_type = TrackFull
            #
            # if self.track['type'] == 'episode':
            #     obj_type = EpisodeFull
            #
            # if obj_type is None:
            #     raise TypeError(f'unkown obj type found {self.track["type"]}')

            obj_type = TrackFull

            self.track = init_with_key_filter(obj_type, self.track)

        if isinstance(self.added_by, dict):
            self.added_by = init_with_key_filter(spotframework.model.user.PublicUser, self.added_by)

        if isinstance(self.added_at, str):
            self.added_at = datetime.strptime(self.added_at, '%Y-%m-%dT%H:%M:%S%z')


@dataclass
class PlayedTrack:
    played_at: datetime
    context: Context
    track: SimplifiedTrack

    def __post_init__(self):
        if isinstance(self.context, dict):
            self.context = init_with_key_filter(Context, self.context)
        if isinstance(self.track, dict):
            self.track = init_with_key_filter(TrackFull, self.track)
        if isinstance(self.played_at, str):
            self.played_at = datetime.strptime(self.played_at, '%Y-%m-%dT%H:%M:%S%z')


@dataclass
class AudioFeatures:
    acousticness: float
    analysis_url: str
    danceability: float
    duration_ms: int
    energy: float
    uri: Uri
    instrumentalness: float
    key: int
    liveness: float
    loudness: float
    mode: AudioFeatures.Mode
    speechiness: float
    tempo: float
    time_signature: int
    track_href: str
    valence: float
    type: str
    id: str

    class Mode(Enum):
        MINOR = 0
        MAJOR = 1

    def __post_init__(self):
        self.acousticness = self.check_float(self.acousticness)
        self.danceability = self.check_float(self.danceability)
        self.energy = self.check_float(self.energy)
        self.instrumentalness = self.check_float(self.instrumentalness)
        self.liveness = self.check_float(self.liveness)

        if self.mode == 0:
            self.mode = self.Mode.MINOR
        elif self.mode == 1:
            self.mode = self.Mode.MAJOR
        else:
            raise ValueError('illegal value for mode')
        self.speechiness = self.check_float(self.speechiness)
        self.valence = self.check_float(self.valence)

        if isinstance(self.mode, int):
            self.mode = AudioFeatures.Mode(self.mode)

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
    def key_str(self) -> str:
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
        if legend.get(self.key, None):
            return legend.get(self.key, None)
        else:
            raise ValueError('key value out of bounds')

    @key_str.setter
    def key_str(self, value):
        if isinstance(value, int):
            if 0 <= value <= 11:
                self.key = value
            else:
                raise ValueError('key value out of bounds')
        else:
            raise ValueError('key value not integer')

    @property
    def is_live(self):
        if self.liveness is not None:
            if self.liveness > 0.8:
                return True
            else:
                return False
        else:
            raise ValueError('no value for liveness')

    @property
    def is_instrumental(self):
        if self.instrumentalness is not None:
            if self.instrumentalness > 0.5:
                return True
            else:
                return False
        else:
            raise ValueError('no value for instrumentalness')

    @property
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


@dataclass
class Context:
    uri: Union[str, Uri]
    type: str = None
    href: str = None
    external_urls: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)
        if self.uri:
            if self.uri.object_type not in [Uri.ObjectType.album, Uri.ObjectType.artist, Uri.ObjectType.playlist]:
                raise TypeError('context uri must be one of album, artist, playlist')

    def __eq__(self, other):
        return isinstance(other, Context) and other.uri == self.uri

    def __str__(self):
        return str(self.uri)


@dataclass
class Device:

    class DeviceType(Enum):
        COMPUTER = 1
        TABLET = 2
        SMARTPHONE = 3
        SPEAKER = 4
        TV = 5
        AVR = 6
        STB = 7
        AUDIODONGLE = 8
        GAMECONSOLE = 9
        CASTVIDEO = 10
        CASTAUDIO = 11
        AUTOMOBILE = 12
        UNKNOWN = 13

    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: DeviceType
    volume_percent: int

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = Device.DeviceType[self.type.upper()]

    def __str__(self):
        return self.name


@dataclass
class CurrentlyPlaying:
    context: Context
    timestamp: str
    progress_ms: int
    is_playing: bool
    item: spotframework.model.track.SimplifiedTrack
    device: Device
    shuffle_state: bool
    repeat_state: bool
    currently_playing_type: str
    actions: dict

    def __post_init__(self):
        if isinstance(self.context, Context):
            self.context = init_with_key_filter(Context, self.context)

        if isinstance(self.item, spotframework.model.track.SimplifiedTrack):
            self.item = init_with_key_filter(spotframework.model.track.SimplifiedTrack, self.item)

        if isinstance(self.device, Device):
            self.device = init_with_key_filter(Device, self.device)

    def __eq__(self, other):
        return isinstance(other, CurrentlyPlaying) and other.item == self.item and other.context == self.context

    @staticmethod
    def _format_duration(duration):
        total_seconds = duration / 1000
        minutes = int((total_seconds/60) % 60)
        seconds = int(total_seconds % 60)
        return f'{minutes}:{seconds}'

    def __str__(self):
        if self.is_playing:
            playing = 'playing'
        else:
            playing = '(paused)'

        return f'{playing} {self.item} on {self.device} from {self.context} ({self._format_duration(self.progress_ms)})'


@dataclass
class RecommendationsSeed:
    afterFilteringSize: int
    afterRelinkingSize: int
    href: str
    id: str
    initialPoolSize: int
    type: str


@dataclass
class Recommendations:
    seeds: List[RecommendationsSeed]
    tracks: List[spotframework.model.track.SimplifiedTrack]

    def __post_init__(self):
        if all((isinstance(i, dict) for i in self.seeds)):
            self.seeds = [init_with_key_filter(RecommendationsSeed, i) for i in self.seeds]

        if all((isinstance(i, dict) for i in self.tracks)):
            self.tracks = [init_with_key_filter(spotframework.model.track.TrackFull, i) for i in self.tracks]