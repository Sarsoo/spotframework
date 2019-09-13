from spotframework.util.console import Color


class User:
    def __init__(self,
                 username: str,

                 href: str = None,
                 uri: str = None,

                 display_name: str = None,
                 ext_spotify: str = None):
        self.username = username

        self.href = href
        self.uri = uri

        self.display_name = display_name
        self.ext_spotify = ext_spotify

    def __str__(self):
        return f'{self.username}'

    def __repr__(self):
        return Color.RED + Color.BOLD + 'User' + Color.END + \
               f': {self.username}, {self.display_name}, {self.uri}'
