from spotframework.net.network import Network, SpotifyNetworkException
from spotframework.model.track import SimplifiedTrack, Context, Device
from spotframework.model.album import AlbumFull
from spotframework.model.playlist import FullPlaylist
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
        try:
            return self.net.get_available_devices()
        except SpotifyNetworkException as e:
            logger.error(f'error retrieving current devices - {e}')

    @property
    def status(self):
        try:
            new_status = self.net.get_player()
            if new_status:
                self.last_status = new_status
                return self.last_status
        except SpotifyNetworkException as e:
            logger.error(f'error retrieving current devices - {e}')

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

        try:
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
        except SpotifyNetworkException as e:
            logger.error(f'error playing - {e}')

    def change_device(self, device: Device):
        try:
            self.net.change_playback_device(device.id)
        except SpotifyNetworkException as e:
            logger.error(f'error changing device to {device.name} - {e}')

    def pause(self):
        try:
            self.net.pause()
        except SpotifyNetworkException as e:
            logger.error(f'error pausing - {e}')

    def toggle_playback(self):
        status = self.status
        try:
            if status:
                if status.is_playing:
                    self.pause()
                else:
                    self.play()
            else:
                logger.warning('no current playback, playing')
                self.play()
        except SpotifyNetworkException as e:
            logger.error(f'error toggling playback - {e}')

    def next(self):
        try:
            self.net.next()
        except SpotifyNetworkException as e:
            logger.error(f'error skipping track - {e}')

    def previous(self):
        try:
            self.net.previous()
        except SpotifyNetworkException as e:
            logger.error(f'error reversing track - {e}')

    def shuffle(self, state=None):
        if state is not None:
            if isinstance(state, bool):
                try:
                    self.net.set_shuffle(state)
                except SpotifyNetworkException as e:
                    logger.error(f'error setting shuffle - {e}')
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
            try:
                if device:
                    self.net.set_volume(value, deviceid=device.id)
                else:
                    self.net.set_volume(value)
            except SpotifyNetworkException as e:
                logger.error(f'error setting volume to {value} - {e}')
        else:
            logger.error(f'{value} not between 0 and 100')
