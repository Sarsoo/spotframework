from spotframework.model.service import CurrentlyPlaying
from spotframework.net.network import Network

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Listener:
    def __init__(self,
                 net: Network,
                 request_size: int = 20,
                 max_recent_tracks: int = None):
        self.net = net
        self.request_size = request_size
        self.max_recent_tracks = max_recent_tracks

        self.recent_tracks = []
        self.prev_now_playing: Optional[CurrentlyPlaying] = None
        self.now_playing: Optional[CurrentlyPlaying] = net.get_player()

        self.on_playback_change = []

    def update_now_playing(self):
        logger.debug('updating now playing')
        live_now_playing = self.net.get_player()

        if self.now_playing is None and live_now_playing is None:
            return

        if live_now_playing != self.now_playing:
            self.prev_now_playing = self.now_playing
            self.now_playing = live_now_playing
            for func in self.on_playback_change:
                func(live_now_playing)
        else:
            self.now_playing = live_now_playing

    def update_recent_tracks(self):
        logger.debug('updating recent tracks')
        tracks = self.net.get_recently_played_tracks(response_limit=self.request_size)
        if tracks is not None:
            for track in tracks:
                if track.played_at not in [i.played_at for i in self.recent_tracks]:
                    self.recent_tracks.append(track)

            self.recent_tracks.sort(key=lambda x: x.played_at)
            if self.max_recent_tracks is not None:
                self.recent_tracks = self.recent_tracks[-self.max_recent_tracks:]
        else:
            logger.error('no recent tracks returned')
