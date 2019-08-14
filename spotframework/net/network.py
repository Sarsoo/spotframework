import requests
import random
import logging
from . import const
from spotframework.model.playlist import Playlist

limit = 50

logger = logging.getLogger(__name__)


class Network:

    def __init__(self, user):
        self.user = user

    def _make_get_request(self, method, url, params=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.get(const.api_url + url, params=params, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} get {req.status_code}')
            return req.json()
        else:
            error_text = req.json()['error']['message']
            logger.error(f'{method} get {req.status_code} {error_text}')

        return None

    def _make_post_request(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.post(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} post {req.status_code}')
            return req
        else:
            error_text = str(req.text)
            logger.error(f'{method} post {req.status_code} {error_text}')

        return None

    def _make_put_request(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.put(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} put {req.status_code}')
            return req
        else:
            error_text = str(req.text)
            logger.error(f'{method} put {req.status_code} {error_text}')

        return None

    def get_playlist(self, playlistid):

        logger.info(f"{playlistid}")

        tracks = self.get_playlist_tracks(playlistid)

        playlist = Playlist(playlistid)
        playlist.tracks += tracks

        return playlist

    def create_playlist(self, username, name='New Playlist', public=True, collaborative=False, description=None):

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description:
            json['description'] = description

        req = self._make_post_request('createPlaylist', f'users/{username}/playlists', json=json)

        if 200 <= req.status_code < 300:
            return req.json()

    def get_playlists(self, offset=0):

        logger.info(f"{offset}")

        playlists = []

        params = {'offset': offset, 'limit': limit}

        resp = self._make_get_request('getPlaylists', 'me/playlists', params=params)

        if resp:

            for responseplaylist in resp['items']:

                playlist = Playlist(responseplaylist['id'], responseplaylist['uri'])
                playlist.name = responseplaylist['name']
                playlist.userid = responseplaylist['owner']['id']

                playlists.append(playlist)

            # playlists = playlists + resp['items']

            if resp['next']:
                playlists += self.get_playlists(offset + limit)

            return playlists

        else:
            return None

    def get_user_playlists(self):

        logger.info('retrieved')

        return list(filter(lambda x: x.userid == self.user.username, self.get_playlists()))

    def get_playlist_tracks(self, playlistid, offset=0):

        logger.info(f"{playlistid}{' ' + str(offset) if offset is not 0 else ''}")

        tracks = []

        params = {'offset': offset, 'limit': limit}

        resp = self._make_get_request('getPlaylistTracks', f'playlists/{playlistid}/tracks', params=params)

        if resp and resp.get('items'):
            tracks += resp['items']
        else:
            logger.warning(f'{playlistid} no response or items')

        if resp.get('next', None):
            tracks += self.get_playlist_tracks(playlistid, offset + limit)

        return tracks

    def get_available_devices(self):

        logger.info("retrieved")

        return self._make_get_request('getAvailableDevices', 'me/player/devices')

    def get_player(self):

        logger.info("retrieved")

        return self._make_get_request('getPlayer', 'me/player')

    def get_device_id(self, devicename):

        logger.info(f"{devicename}")

        return next((i for i in self.get_available_devices()['devices'] if i['name'] == devicename), None)['id']

    def play(self, uri=None, uris=None, deviceid=None):

        logger.info(f"{uri}{' ' + deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        if uri and uris:
            raise Exception('wont take both context uri and uris')

        if uri:
            payload = {'context_uri': uri}

        if uris:
            payload = {'uris': uris[:200]}

        if not uri and not uris:
            raise Exception('need either context uri or uris')

        req = self._make_put_request('play', 'me/player/play', params=params, json=payload)

    def pause(self, deviceid=None):

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_put_request('pause', 'me/player/pause', params=params)

    def next(self, deviceid=None):

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_post_request('next', 'me/player/next', params=params)

    def set_shuffle(self, state, deviceid=None):

        logger.info(f"{state}{' ' + deviceid if deviceid is not None else ''}")

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self._make_put_request('setShuffle', 'me/player/shuffle', params=params)

    def set_volume(self, volume, deviceid=None):

        logger.info(f"{volume}{' ' + deviceid if deviceid is not None else ''}")

        if volume.isdigit() and 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}

            if deviceid is not None:
                params['device_id'] = deviceid

            req = self._make_put_request('setVolume', 'me/player/volume', params=params)

        else:
            logger.error(f"{volume} not accepted value")

    def replace_playlist_tracks(self, playlistid, uris):

        logger.info(f"{playlistid}")

        headers = {"Content-Type": "application/json"}

        json = {"uris": uris[:100]}

        req = self._make_put_request('replacePlaylistTracks', f'playlists/{playlistid}/tracks', json=json, headers=headers)

        if req is not None:
            resp = req.json()

            if len(uris) > 100:
                self.add_playlist_tracks(playlistid, uris[100:])

    def change_playlist_details(self, playlistid, name=None, public=None, collaborative=None, description=None):

        logger.info(f"{playlistid}")

        headers = {"Content-Type": "application/json"}

        json = {}

        if name is not None:
            json['name'] = name

        if public is not None:
            json['public'] = public

        if collaborative is not None:
            json['collaborative'] = collaborative

        if description is not None:
            json['description'] = description

        req = self._make_put_request('changePlaylistDetails', f'playlists/{playlistid}', json=json, headers=headers)
        return req

    def add_playlist_tracks(self, playlistid, uris):

        logger.info(f"{playlistid}")

        headers = {"Content-Type": "application/json"}

        json = {"uris": uris[:100]}

        req = self._make_post_request('addPlaylistTracks', f'playlists/{playlistid}/tracks', json=json, headers=headers)

        if req is not None:
            resp = req.json()

            if len(uris) > 100:

                self.add_playlist_tracks(playlistid, uris[100:])

    def get_recommendations(self, tracks=None, artists=None, response_limit=10):

        logger.info(f'sample size: {response_limit}')

        params = {'limit': response_limit}

        if tracks:
            random.shuffle(tracks)
            params['seed_tracks'] = tracks[:100]
        if artists:
            random.shuffle(artists)
            params['seed_artists'] = artists[:100]

        return self._make_get_request('getRecommendations', 'recommendations', params=params)
