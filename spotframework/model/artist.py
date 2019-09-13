from typing import List
from spotframework.util.console import Color


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
                 spotify_id: str = None,
                 uri: str = None,

                 genres: List[str] = None,

                 popularity: int = None
                 ):
        super().__init__(name)

        self.href = href
        self.spotify_id = spotify_id
        self.uri = uri

        self.genres = genres

        self.popularity = popularity

    def __repr__(self):
        return Color.PURPLE + Color.BOLD + 'SpotifyArtist' + Color.END + \
               f': {self.name}, {self.uri}'