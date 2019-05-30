import spotframework.net.const as const
import spotframework.net.network as network
import spotframework.net.user as user
import spotframework.log.log as log
import spotframework.io.json as json

import requests

import os

if __name__ == '__main__':

    try:
        if os.path.exists(os.path.join(const.config_path, 'playlists.json')):

            data = json.loadJson(os.path.join(const.config_path, 'playlists.json'))

            net = network.network(user.User())
            playlists = net.getUserPlaylists()

            for tomake in data['playlists']:

                log.log("generatePlaylist", tomake['name'])

                tracks = []

                for part in tomake['playlists']:

                    play = next((i for i in playlists if i.name == part), None)

                    if play is not None:

                        if len(play.tracks) == 0:
                            log.log("pulling tracks for {}".format(play.name))
                            play.tracks = net.getPlaylistTracks(play.playlistid)

                        tracks += [i for i in play.tracks if i['track']['uri'] not in [j['track']['uri'] for j in tracks] and i['is_local'] is False]

                    else:
                        log.log("requested playlist {} not found".format(part))
                        if 'SLACKHOOK' in os.environ:
                            requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: {} not found".format(part)})

                if 'shuffle' in tomake:
                    if tomake['shuffle'] is True:
                        import random
                        random.shuffle(tracks)
                    else:
                        tracks.sort(key=lambda x: x['track']['album']['release_date'], reverse=True)
                else:
                    tracks.sort(key=lambda x: x['track']['album']['release_date'], reverse=True)

                net.replacePlaylistTracks(tomake['id'], [i['track']['uri'] for i in tracks])
                net.changePlaylistDetails(tomake['id'], description=' / '.join(tomake['playlists']))
        else:
            log.log("config json not found")
            if 'SLACKHOOK' in os.environ:
                requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: config json not found"})

        log.dumpLog()
    except:
        log.dumpLog()
