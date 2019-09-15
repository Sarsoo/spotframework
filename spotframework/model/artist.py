from typing import List, Union
from spotframework.util.console import Color
from spotframework.model.uri import Uri


class Artist:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return Color.PURPLE + Color.BOLD + 'Artist' + Color.END + \
               f': {self.name}'


class SpotifyArtist(Artist):
    def __init__(self,
                 name: str,

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 genres: List[str] = None,

                 popularity: int = None
                 ):
        super().__init__(name)

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri

        self.genres = genres

        self.popularity = popularity

    def __repr__(self):
        return Color.PURPLE + Color.BOLD + 'SpotifyArtist' + Color.END + \
               f': {self.name}, {self.uri}'
