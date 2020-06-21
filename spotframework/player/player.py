from spotframework.net.network import Network
from spotframework.model.track import SimplifiedTrack, Context, Device
from spotframework.model.album import AlbumFull
from spotframework.model.playlist import FullPlaylist
from spotframework.model.uri import Uri
from typing import List, Union
import logging
logger = logging.getLogger(__name__)


class Player:

    def __init__(self,
                 net: Network):
        self.net = net
        self.last_status = None

    def __str__(self):
        return f'{self.net.user.user.display_name} - {self.status}'

    def __repr__(self):
        return f'Player: {self.net.user} - {self.status}'

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
             context: Union[Context, AlbumFull, FullPlaylist] = None,
             tracks: List[SimplifiedTrack] = None,
             uris: List = None,
             device: Device = None,
             device_name: str = None):
        if device_name:
            searched_device = next((i for i in self.available_devices if i.name == device_name), None)
            if searched_device:
                device = searched_device

        if context and (tracks or uris):
            raise Exception('cant execute context and track list')
        if context:
            if device:
                self.net.play(uri=context.uri, deviceid=device.id)
            else:
                self.net.play(uri=context.uri)
        elif tracks or uris:

            if tracks is None:
                tracks = []

            if uris is None:
                uris = []

            if device:
                self.net.play(uris=[i.uri for i in tracks] + uris, deviceid=device.id)
            else:
                self.net.play(uris=[i.uri for i in tracks] + uris)
        else:
            self.net.play()

    def change_device(self, device: Device):
        self.net.change_playback_device(device.id)

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
            if status.shuffle_state:
                self.shuffle(state=False)
            else:
                self.shuffle(state=True)

    def volume(self, value: int, device: Device = None):

        if 0 <= int(value) <= 100:
            if device:
                self.net.set_volume(value, deviceid=device.id)
            else:
                self.net.set_volume(value)
        else:
            logger.error(f'{value} not between 0 and 100')
