from dataclasses import dataclass
from typing import List, Union
from spotframework.model.uri import Uri
from spotframework.model.service import Image

from spotframework.model import init_with_key_filter


@dataclass
class SimplifiedArtist:
    name: str
    external_urls: dict
    href: str
    id: str
    uri: Union[str, Uri]
    type: str

    def __post_init__(self):
        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type not in [Uri.ObjectType.artist, Uri.ObjectType.show]:
                raise TypeError('provided uri not for an artist')

    def __str__(self):
        return f'{self.name}'


@dataclass
class ArtistFull(SimplifiedArtist):
    genres: List[str]
    images: List[Image]
    popularity: int

    def __post_init__(self):
        super().__post_init__()

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [init_with_key_filter(Image, i) for i in self.images]
