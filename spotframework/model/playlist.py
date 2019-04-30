

class playlist:

    def __init__(self, playlistid, name=None, userid=None):
        self.tracks = []
        self.name = name
        self.playlistid = playlistid
        self.userid = userid
