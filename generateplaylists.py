import spotframework.net.const as const
from spotframework.net.network import Network
from spotframework.net.user import User
import spotframework.io.json as json
import spotframework.util.monthstrings as monthstrings
from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.engine.filter.shuffle import Shuffle
from spotframework.engine.filter.sortreversereleasedate import SortReverseReleaseDate
from spotframework.engine.filter.deduplicatebyid import DeduplicateByID
from spotframework.engine.filter.deduplicatebyname import DeduplicateByName

import os
import datetime
import sys
import logging

import requests


logger = logging.getLogger('spotframework')

log_format = '%(asctime)s %(levelname)s %(name)s - %(funcName)s - %(message)s'

file_handler = logging.FileHandler(".spot/generate_playlists.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def update_super_playlist(engine, data_dict):

    logger.info(f"makePlaylist {data_dict['name']}")

    processors = [DeduplicateByID()]

    if 'shuffle' in data_dict:
        if data_dict['shuffle'] is True:
            processors.append(Shuffle())
        else:
            processors.append(SortReverseReleaseDate())
    else:
        processors.append(SortReverseReleaseDate())

    tracks = engine.make_playlist(data_dict['playlists'], processors)

    engine.execute_playlist(tracks, data_dict['id'])
    engine.change_description(data_dict['playlists'], data_dict['id'])


def update_recents_playlist(engine, data):

    recents_id = data['recents']['id']
    boundary_date = datetime.datetime.now() - datetime.timedelta(days=data['recents']['boundary'])

    recent_parts = []

    if 'use_marked_playlists' in data['recents']:
        if data['recents']['use_marked_playlists']:
            for playlist in [i for i in data['playlists'] if 'include_in_recents' in i]:
                if playlist['include_in_recents']:
                    recent_parts += [i for i in playlist['playlists']]

    else:
        for playlist in [i for i in data['playlists'] if 'include_in_recents' in i]:
            if playlist['include_in_recents']:
                recent_parts += [i for i in playlist['playlists']]

    if 'playlists' in data['recents']:
        recent_parts += data['recents']['playlists']

    if 'exclude' in data['recents']:
        for exclusion in data['recents']['exclude']:
            recent_parts.remove(exclusion)

    processors = [DeduplicateByName(), SortReverseReleaseDate()]

    recent_tracks = engine.get_recent_playlist(boundary_date, recent_parts, processors)
    engine.execute_playlist(recent_tracks, recents_id)
    engine.change_description([monthstrings.get_this_month(), monthstrings.get_last_month()], data['recents']['id'])


def go():

    try:
        if os.path.exists(os.path.join(const.config_path, 'config.json')):

            data = json.load_json(os.path.join(const.config_path, 'config.json'))

            to_execute = []
            not_found = []

            available_specials = ['recents']
            specials_to_execute = []

            if len(sys.argv) > 1:
                for arg in sys.argv[1:]:
                    for playlist in data['playlists']:
                        if arg.lower() == playlist['name'].lower():
                            to_execute.append(playlist)
                            break
                    else:
                        if arg in available_specials:
                            specials_to_execute.append(arg)
                        else:
                            not_found.append(arg)
            else:
                to_execute = data['playlists']
                specials_to_execute = ['recents']

            if len(not_found) > 0:
                logger.error(f'arg not found {not_found}')

            if len(to_execute) <= 0 and len(specials_to_execute) <= 0:
                logger.critical('none to execute, terminating')
                return

            net = Network(User(os.environ['SPOTCLIENT'],
                               os.environ['SPOTSECRET'],
                               os.environ['SPOTACCESS'],
                               os.environ['SPOTREFRESH']))

            engine = PlaylistEngine(net)
            engine.load_user_playlists()

            for super_playlist in to_execute:
                update_super_playlist(engine, super_playlist)

            if 'recents' in data and 'recents' in specials_to_execute:
                update_recents_playlist(engine, data)

        else:
            logger.critical("config json not found")
            if 'SLACKHOOK' in os.environ:
                requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: config json not found"})

    except Exception as e:
        logger.exception("exception occured")
        if 'SLACKHOOK' in os.environ:
            requests.post(os.environ['SLACKHOOK'], json={"text": f"spot playlists: exception occured {e}"})


if __name__ == '__main__':
    go()
