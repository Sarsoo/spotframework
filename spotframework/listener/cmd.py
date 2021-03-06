from cmd import Cmd
import functools
import logging
from typing import Optional

from spotframework.util.console import Color
from spotframework.net.network import Network
from spotframework.listener.thread import ListenerThread

logger = logging.getLogger(__name__)


def check_thread(func):
    @functools.wraps(func)
    def check_thread_wrapper(self, *args, **kwargs):
        if self.listen_thread is not None:
            return func(self, *args, **kwargs)
        else:
            print('>> not running')

    return check_thread_wrapper


def check_last_dataset(func):
    @functools.wraps(func)
    def check_last_dataset_wrapper(self, *args, **kwargs):
        if self.last_dataset is not None:
            return func(self, *args, **kwargs)
        else:
            print('>> not running')

    return check_last_dataset_wrapper


class ListenCmd(Cmd):
    """cmd utility class for interacting with Listener and associated async thread"""

    intro = 'listener... ? for help'
    prompt = '(listen)> '

    dt_format = "%-H:%M:%S %-d %b %-y"

    def __init__(self, net: Network, log_stream_handler=None):
        Cmd.__init__(self)
        self.net = net
        self.listen_thread: Optional[ListenerThread] = None
        self.last_listener = None

        self.verbose = False
        self.log_stream_handler = log_stream_handler

    def start_listener(self):
        """start listener thread if not running, else restart thread"""
        if self.listen_thread is not None:
            logger.info('restarting')
            print('>> restarting listener')
            self.stop_listener()

        logger.info('starting')
        print('>> starting listener')
        self.listen_thread = ListenerThread(self.net)
        self.listen_thread.listener.on_playback_change.append(lambda x: print(f'playback changed -> {x}'))
        self.listen_thread.start()

    @check_thread
    def stop_listener(self):
        """kill listener thread"""
        logger.info('stopping')
        print('>> stopping listener')
        self.last_listener = self.listen_thread.listener
        self.listen_thread.stop()

    def print_tracks(self, tracks):
        """print played tracks with timecodes

        :param tracks: list of target track objects
        :return: None
        """
        [print(f'({i.played_at.strftime(self.dt_format)}) {Color.BOLD}{Color.RED}{i.name}{Color.END} / '
               f'{i.album.name} / {Color.BOLD}{Color.BLUE}{i.artists_names}{Color.END}')
         for i in tracks]

    def print(self):
        """display previously and currently playing tracks"""
        if self.listen_thread is not None:
            self.print_tracks(self.listen_thread.listener.recent_tracks)
            print('now playing:', self.listen_thread.listener.now_playing)
        elif self.last_listener is not None:
            self.print_tracks(self.last_listener.recent_tracks)
        else:
            print('>> no tracks to print')

    @check_thread
    def set_poll_interval(self, value):
        """set polling interval on background thread

        :param value: new time value in seconds
        :return: None
        """
        if value.isdigit():
            logger.info(f'setting polling interval to {value}')
            print(f'>> interval set to {value}')
            self.listen_thread.sleep_interval = int(value)
        else:
            logger.error(f'{value} is not a valid interval')
            print('>> not a number')

    def do_interval(self, args):
        """set polling interval"""
        self.set_poll_interval(args)

    def do_print(self, args):
        """print recently played tracks"""
        self.print()

    def do_p(self, args):
        """print recently played tracks"""
        self.print()

    def do_listen(self, args):
        """start listener"""
        self.start_listener()

    def do_l(self, args):
        """start listener"""
        self.start_listener()

    def do_stop(self, args):
        """stop listener"""
        self.stop_listener()

    def do_e(self, args):
        """stop listener"""
        self.stop_listener()

    def do_verbose(self, args):
        """toggle verbosity"""
        if self.log_stream_handler is not None:
            self.verbose = not self.verbose
            if self.verbose:
                self.log_stream_handler.setLevel('DEBUG')
            else:
                self.log_stream_handler.setLevel('WARNING')

    @check_thread
    def do_quit(self, args):
        """stop and quit"""
        logger.info('quitting')
        self.stop_listener()
        self.listen_thread.join()
        exit(0)

    @check_thread
    def do_q(self, args):
        """stop and quit"""
        logger.info('quitting')
        self.stop_listener()
        self.listen_thread.join()
        exit(0)

    @check_thread
    def do_status(self, args):
        """stop and quit"""
        if self.listen_thread is not None:
            if self.listen_thread.is_alive():
                print('>> running')
            else:
                print('>> thread dead')
        else:
            print('>> not running')
