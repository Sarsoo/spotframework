from spotframework.util.console import Color
from spotframework.model.uri import Uri
from typing import Union


class User:
    def __init__(self,
                 username: str,

                 href: str = None,
                 uri: Union[str, Uri] = None,

                 display_name: str = None,
                 ext_spotify: str = None):
        self.username = username

        self.href = href
        if isinstance(uri, str):
            self.uri = Uri(uri)
        else:
            self.uri = uri

        self.display_name = display_name
        self.ext_spotify = ext_spotify

    def __str__(self):
        return f'{self.username}'

    def __repr__(self):
        return Color.RED + Color.BOLD + 'User' + Color.END + \
               f': {self.username}, {self.display_name}, {self.uri}'
