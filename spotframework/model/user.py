from typing import Union, List
from dataclasses import dataclass, field
from spotframework.model.uri import Uri
from spotframework.model.service import Image


@dataclass
class PublicUser:
    href: str
    id: str
    uri: Union[str, Uri]
    display_name: str
    external_urls: dict
    type: str

    followers: dict = field(default_factory=dict)
    images: List[Image] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.uri, str):
            self.uri = Uri(self.uri)

        if self.uri:
            if self.uri.object_type != Uri.ObjectType.user:
                raise TypeError('provided uri not for a user')

        if all((isinstance(i, dict) for i in self.images)):
            self.images = [Image(**i) for i in self.images]

    def __str__(self):
        return f'{self.display_name}'


@dataclass
class PrivateUser(PublicUser):
    country: str = None
    email: str = None
    product: str = None

