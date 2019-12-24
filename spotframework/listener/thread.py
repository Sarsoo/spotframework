import threading
import logging

from spotframework.net.network import Network
from spotframework.listener.listener import Listener

logger = logging.getLogger(__name__)


class ListenerThread(threading.Thread):

    def __init__(self,
                 net: Network,
                 sleep_interval: int = 5,
                 request_size: int = 20):
        super(ListenerThread, self).__init__()
        self._stop_event = threading.Event()
        self.sleep_interval = sleep_interval
        self.iterating_actions = []

        self.listener = Listener(net=net, request_size=request_size)

    def stop(self):
        logger.info('stopping thread')
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            self.listener.update_recent_tracks()
            self.listener.update_now_playing()
            for action in self.iterating_actions:
                action()
            self._stop_event.wait(self.sleep_interval)
