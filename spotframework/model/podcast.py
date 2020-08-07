from typing import List, Union
from dataclasses import dataclass
from datetime import datetime

from spotframework.model import init_with_key_filter

from spotframework.model.service import Image
from spotframework.model.uri import Uri

@dataclass
class ResumePoint:
    fully_played: bool
    resume_position_ms: int

@dataclass
class SimplifiedEpisode:
    audio_preview_url: str
    description: str
    duration_ms: int
    explicit: bool
    external_urls: dict
    href: str
    id: str
    images: List[Image]
    is_externally_hosted: bool
    is_playable: bool
    languages: List[str]
    name: str
    release_date: datetime
    release_date_precision: str
    type: str
    uri: Union[str, Uri]
    language: str = None # soon to be deprecated
    resume_point: ResumePoint = None

    def __post_init__(self):

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.episode:
                raise TypeError('provided uri not for an episode')

        if isinstance(self.resume_point, ResumePoint):
            self.resume_point = init_with_key_filter(ResumePoint, self.resume_point)

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [init_with_key_filter(Image, i) for i in self.images]

        if isinstance(self.release_date, str):
            if self.release_date_precision == 'year':
                self.release_date = datetime.strptime(self.release_date, '%Y')
            elif self.release_date_precision == 'month':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m')
            elif self.release_date_precision == 'day':
                self.release_date = datetime.strptime(self.release_date, '%Y-%m-%d')

@dataclass
class SimplifiedShow:
    available_markets: List[str]
    copyrights: List[dict]
    description: str
    explicit: bool
    external_urls: dict
    href: str
    id: str
    images: List[Image]
    is_externally_hosted: bool
    languages: List[str]
    media_type: str
    name: str
    publisher: str
    type: str
    total_episodes: int
    uri: Union[str, Uri]

    def __post_init__(self):

        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.show:
                raise TypeError('provided uri not for an show')

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [init_with_key_filter(Image, i) for i in self.images]

@dataclass
class EpisodeFull(SimplifiedEpisode):
    show: SimplifiedShow = None

    def __post_init__(self):
        super().__post_init__()

        if isinstance(self.show, SimplifiedShow):
            self.show = init_with_key_filter(SimplifiedShow, self.show)

@dataclass
class ShowFull(SimplifiedShow):
    episodes: List[SimplifiedEpisode]

@dataclass
class SavedShow:
    added_at: datetime
    show: ShowFull

    def __post_init__(self):

        if isinstance(self.show, ShowFull):
            self.show = init_with_key_filter(ShowFull, self.show)
