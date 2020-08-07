import functools
from typing import List, Union
import logging

from spotframework.net.network import Network, SpotifyNetworkException
from spotframework.model.track import SimplifiedTrack, Context, Device
from spotframework.model.album import AlbumFull
from spotframework.model.playlist import FullPlaylist

from spotframework.util.decorators import inject_uri

logger = logging.getLogger(__name__)


class Player:
    class Decorators:
        @staticmethod
        def inject_device(_func=None):
            def decorator_inject_device(func):
                @functools.wraps(func)
                def inject_device_wrapper(self, *args, **kwargs):

                    if kwargs.get('device_name'):
                        kwargs['device'] = self.get_device(kwargs['device_name'], 'name')

                        del kwargs['device_name']

                    elif kwargs.get('device_id'):
                        kwargs['device'] = self.get_device(kwargs['device_id'], 'id')

                        del kwargs['device_id']

                    elif kwargs.get('device'):
                        pass

                    return func(self, *args, **kwargs)

                return inject_device_wrapper

            if _func is None:
                return decorator_inject_device
            else:
                return decorator_inject_device(_func)

    def __init__(self,
                 net: Network):
        self.net = net
        self.last_status = None

    def __str__(self):
        return f'{self.net.user.user.id} - {self.status}'

    def __repr__(self):
        return f'Player: {self.net.user} - {self.status}'

    @property
    def available_devices(self):
        try:
            return self.net.get_available_devices()
        except SpotifyNetworkException as e:
            logger.exception(f'error retrieving current devices')
            raise e

    @property
    def status(self):
        try:
            new_status = self.net.get_player()
            if new_status:
                self.last_status = new_status
                return self.last_status
        except SpotifyNetworkException:
            logger.exception(f'error retrieving current devices')

    @inject_uri(flatten_to_uris=True, uri_optional=True, uris_optional=True)
    @Decorators.inject_device
    def play(self,
             context: Union[Context, AlbumFull, FullPlaylist] = None,
             tracks: List[SimplifiedTrack] = None,
             uris: List = None,
             device: Device = None):
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
        except SpotifyNetworkException:
            logger.exception(f'error playing')

    @Decorators.inject_device
    def change_device(self, device: Device):
        try:
            self.net.change_playback_device(device.id)
        except SpotifyNetworkException:
            logger.exception(f'error changing device to {device.name}')

    @Decorators.inject_device
    def pause(self, device = None):
        try:
            if device is not None:
                self.net.pause(deviceid=device.id)
            else:
                self.net.pause()

        except SpotifyNetworkException:
            logger.exception(f'error pausing')

    @Decorators.inject_device
    def toggle_playback(self, device: Device = None):
        status = self.status
        try:
            if status:
                if status.is_playing:
                    self.pause(device=device)
                else:
                    self.play(device=device)
            else:
                logger.warning('no current playback, playing')
                self.play(device=device)
        except SpotifyNetworkException:
            logger.exception(f'error toggling playback')

    @Decorators.inject_device
    def next(self, device: Device = None):
        try:
            if device is not None:
                self.net.next(deviceid=device.id)
            else:
                self.net.next()

        except SpotifyNetworkException:
            logger.exception(f'error skipping track')

    @Decorators.inject_device
    def previous(self, device: Device = None):
        try:
            if device is not None:
                self.net.previous(deviceid=device.id)
            else:
                self.net.previous()

        except SpotifyNetworkException:
            logger.exception(f'error reversing track')

    @Decorators.inject_device
    def shuffle(self, device: Device = None, state=None):
        if state is not None:
            if isinstance(state, bool):
                try:
                    if device is not None:
                        self.net.set_shuffle(deviceid=device.id, state=state)
                    else:
                        self.net.set_shuffle(state=state)

                except SpotifyNetworkException:
                    logger.exception(f'error setting shuffle')
            else:
                raise TypeError(f'{state} is not bool')

        else:
            self.shuffle(device=device, state=not self.status.shuffle_state)


    @Decorators.inject_device
    def volume(self, value: int, device: Device = None):

        if 0 <= int(value) <= 100:
            try:
                if device is not None:
                    self.net.set_volume(value, deviceid=device.id)
                else:
                    self.net.set_volume(value)
            except SpotifyNetworkException:
                logger.exception(f'error setting volume to {value}')
        else:
            logger.error(f'{value} not between 0 and 100')

    def get_device(self, device_in, attr):

        if isinstance(device_in, str):
            try:
                searched_device = next((i for i in self.available_devices if getattr(i, attr) == device_in), None)
                if searched_device is not None:
                    return searched_device
                else:
                    logger.error(f'device not returned for {device_in}, {attr}')

            except SpotifyNetworkException:
                logger.exception(f'error retrieving current devices')

        elif isinstance(device_in, Device): return device_in

        else: raise TypeError(f'invalid uri type provided - {type(device_in)}')
