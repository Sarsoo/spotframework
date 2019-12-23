import threading
import logging
from typing import Optional

from spotframework.net.network import Network
from spotframework.model.service import CurrentlyPlaying

logger = logging.getLogger(__name__)


class ListenerThread(threading.Thread):

    def __init__(self,
                 net: Network,
                 sleep_interval: int = 5,
                 request_size: int = 5):
        super(ListenerThread, self).__init__()
        self._stop_event = threading.Event()

        self.net = net

        self.sleep_interval = sleep_interval
        self.request_size = request_size

        self.recent_tracks = []
        self.prev_now_playing: Optional[CurrentlyPlaying] = None
        self.now_playing: Optional[CurrentlyPlaying] = net.get_player()

        self.on_playback_change = []

    def stop(self):
        logger.info('stopping thread')
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def update_now_playing(self):
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
        logger.debug('pulling tracks')
        tracks = self.net.get_recently_played_tracks(response_limit=self.request_size)
        for track in tracks:
            if track.played_at not in [i.played_at for i in self.recent_tracks]:
                self.recent_tracks.append(track)

        self.recent_tracks.sort(key=lambda x: x.played_at)

    def run(self):
        while not self.stopped():
            self.update_recent_tracks()
            self.update_now_playing()
            self._stop_event.wait(self.sleep_interval)
