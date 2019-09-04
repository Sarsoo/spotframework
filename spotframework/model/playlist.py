from spotframework.model.user import User


class Playlist:

    def __init__(self,
                 playlistid: str,

                 name: str = None,
                 owner: User = None,
                 description: str = None,

                 href: str = None,
                 uri: str = None,

                 collaborative: bool = None,
                 public: bool = None,
                 ext_spotify: str = None):
        self.tracks = []
        self.name = name

        self.playlist_id = playlistid
        self.owner = owner
        self.description = description

        self.href = href
        self.uri = uri

        self.collaborative = collaborative
        self.public = public
        self.ext_spotify = ext_spotify

    def has_tracks(self):
        if len(self.tracks) > 0:
            return True
        else:
            return False
