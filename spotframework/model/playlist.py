

class Playlist:

    def __init__(self, playlistid, uri=None, name=None, userid=None):
        self.tracks = []
        self.name = name
        self.playlistid = playlistid
        self.userid = userid
        self.uri = uri

    def has_tracks(self):
        if len(self.tracks) > 0:
            return True
        else:
            return False
