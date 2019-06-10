import spotframework.net.const as const
import spotframework.net.network as network
import spotframework.net.user as user
import spotframework.log.log as log
import spotframework.io.json as json
import spotframework.util.monthstrings as monthstrings
from spotframework.engine.playlistengine import PlaylistEngine
from spotframework.engine.filter.shuffle import Shuffle
from spotframework.engine.filter.sortreversereleasedate import SortReverseReleaseDate
from spotframework.engine.filter.deduplicatebyid import DeduplicateByID
from spotframework.engine.filter.deduplicatebyname import DeduplicateByName

import datetime

import requests

import os

if __name__ == '__main__':

    try:
        if os.path.exists(os.path.join(const.config_path, 'playlists.json')):

            data = json.loadJson(os.path.join(const.config_path, 'playlists.json'))

            net = network.network(user.User())

            engine = PlaylistEngine(net)
            engine.load_user_playlists()

            for tomake in data['playlists']:

                log.log("makePlaylist", tomake['name'])

                processors = [DeduplicateByID()]

                if 'shuffle' in tomake:
                    if tomake['shuffle'] is True:
                        processors.append(Shuffle())
                    else:
                        processors.append(SortReverseReleaseDate())
                else:
                    processors.append(SortReverseReleaseDate())

                tracks = engine.make_playlist(tomake['playlists'], processors)

                engine.execute_playlist(tracks, tomake['id'])
                engine.change_description(tomake['playlists'], tomake['id'])

            if 'recents' in data:
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

                processors = [DeduplicateByName(), SortReverseReleaseDate()]

                recent_tracks = engine.get_recent_playlist(boundary_date, recent_parts, processors)
                engine.execute_playlist(recent_tracks, data['recents']['id'])
                engine.change_description([monthstrings.get_this_month(),
                                           monthstrings.get_last_month()]
                                          , data['recents']['id'])

        else:
            log.log("config json not found")
            if 'SLACKHOOK' in os.environ:
                requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: config json not found"})

        log.dumpLog()
    except Exception:
        log.log("exception occured")
        if 'SLACKHOOK' in os.environ:
            requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: exception occured"})
        log.dumpLog()
