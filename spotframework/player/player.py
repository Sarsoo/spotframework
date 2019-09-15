from spotframework.net.network import Network
from spotframework.model.track import SpotifyTrack
from spotframework.model.album import SpotifyAlbum
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.model.service import Context, Device
from typing import List, Union
import logging
logger = logging.getLogger(__name__)


class Player:

    def __init__(self,
                 net: Network):
        self.net = net
        self.user = net.user
        self.last_status = None

    def __str__(self):
        return f'{self.user.username} - {self.status}'

    def __repr__(self):
        return f'Player: {self.user} - {self.status}'

    @property
    def available_devices(self):
        return self.net.get_available_devices()

    @property
    def status(self):
        new_status = self.net.get_player()
        if new_status:
            self.last_status = new_status
            return self.last_status

    def play(self,
             context: Union[Context, SpotifyAlbum, SpotifyPlaylist] = None,
             tracks: List[SpotifyTrack] = None,
             device: Device = None):
        if context and tracks:
            raise Exception('cant execute context and track list')
        if context:
            if device:
                self.net.play(uri=context.uri, deviceid=device.device_id)
            else:
                self.net.play(uri=context.uri)
        elif tracks:
            if device:
                self.net.play(uris=[i.uri for i in tracks], deviceid=device.device_id)
            else:
                self.net.play(uris=[i.uri for i in tracks])
        else:
            self.net.play()

    def change_device(self, device: Device):
        self.net.change_playback_device(device.device_id)

    def pause(self):
        self.net.pause()

    def toggle_playback(self):
        status = self.status
        if status:
            if status.is_playing:
                self.pause()
            else:
                self.play()
        else:
            logger.warning('no current playback, playing')
            self.play()

    def next(self):
        self.net.next()

    def previous(self):
        self.net.previous()

    def shuffle(self, state=None):
        if state is not None:
            if isinstance(state, bool):
                self.net.set_shuffle(state)
            else:
                raise TypeError(f'{state} is not bool')
        else:
            status = self.status
            if status.shuffle:
                self.shuffle(state=False)
            else:
                self.shuffle(state=True)

    def set_volume(self, value: int, device: Device = None):

        if 0 <= int(value) <= 100:
            if device:
                self.net.set_volume(value, deviceid=device.device_id)
            else:
                self.net.set_volume(value)
        else:
            logger.error(f'{value} not between 0 and 100')
