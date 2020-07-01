from spotframework.model.track import CurrentlyPlaying
from spotframework.net.network import Network, SpotifyNetworkException

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Listener:
    """Stateful storage of spotify recent listening history and currently playing"""
    
    def __init__(self,
                 net: Network,
                 request_size: int = 20,
                 max_recent_tracks: int = None):
        self.net = net
        self.request_size = request_size
        self.max_recent_tracks = max_recent_tracks

        self.recent_tracks = []
        self.prev_now_playing: Optional[CurrentlyPlaying] = None
        self.now_playing = None
        try:
            self.now_playing: Optional[CurrentlyPlaying] = net.get_player()
        except SpotifyNetworkException:
            logger.exception(f'error occured retrieving currently playing')

        self.on_playback_change = []

    def update_now_playing(self):
        """update currently playing values"""
        logger.debug('updating now playing')

        try:
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

        except SpotifyNetworkException:
            logger.exception(f'error occured retrieving currently playing')

    def update_recent_tracks(self):
        """retrieve recently played tracks and merge with previously stored"""
        logger.debug('updating recent tracks')

        try:
            tracks = self.net.get_recently_played_tracks(response_limit=self.request_size)
            for track in tracks:
                if track.played_at not in [i.played_at for i in self.recent_tracks]:
                    self.recent_tracks.append(track)

            self.recent_tracks.sort(key=lambda x: x.played_at)
            if self.max_recent_tracks is not None:
                self.recent_tracks = self.recent_tracks[-self.max_recent_tracks:]

        except SpotifyNetworkException:
            logger.exception(f'error occured retrieving recent tracks')
