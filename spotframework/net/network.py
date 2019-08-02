import requests
from . import const
from spotframework.model.playlist import Playlist
import spotframework.log.log as log

limit = 50


class Network:

    def __init__(self, user):
        self.user = user

    def _make_get_request(self, method, url, params=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.get(const.api_url + url, params=params, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'get', str(req.status_code))
            return req.json()
        else:
            log.log(method, 'get', str(req.status_code), req.text)

        return None

    def _make_post_request(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.post(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'post', str(req.status_code))
            return req
        else:
            log.log(method, 'post', str(req.status_code), req.text)

        return None

    def _make_put_request(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.put(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'put', str(req.status_code))
            return req
        else:
            log.log(method, 'put', str(req.status_code), req.text)

        return None

    def get_playlist(self, playlistid, tracksonly=False):

        log.log("getPlaylist", playlistid)

        tracks = self.get_playlist_tracks(playlistid)

        playlist = Playlist(playlistid)
        playlist.tracks += tracks

        if not tracksonly:
            pass

        return playlist

    def get_playlists(self, offset=0):

        log.log("getPlaylists", offset)

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

        log.log("getUserPlaylists")

        return list(filter(lambda x: x.userid == self.user.username, self.get_playlists()))

    def get_playlist_tracks(self, playlistid, offset=0):

        log.log("getPlaylistTracks", playlistid, offset)

        tracks = []

        params = {'offset': offset, 'limit': limit}

        resp = self._make_get_request('getPlaylistTracks', f'playlists/{playlistid}/tracks', params=params)

        tracks += resp['items']

        if resp['next']:
            tracks += self.get_playlist_tracks(playlistid, offset + limit)

        return tracks

    def get_available_devices(self):

        log.log("getAvailableDevices")

        return self._make_get_request('getAvailableDevices', 'me/player/devices')

    def get_player(self):

        log.log("getPlayer")

        return self._make_get_request('getPlayer', 'me/player')

    def get_device_id(self, devicename):

        log.log("getDeviceID", devicename)

        return next((i for i in self.get_available_devices()['devices'] if i['name'] == devicename), None)['id']

    def play(self, uri, deviceid=None):

        log.log("play", uri, deviceid)

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        payload = {'context_uri': uri}

        req = self._make_put_request('play', 'me/player/play', params=params, json=payload)

    def pause(self, deviceid=None):

        log.log("pause", deviceid)

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_put_request('pause', 'me/player/pause', params=params)

    def next(self, deviceid=None):

        log.log("next", deviceid)

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_post_request('next', 'me/player/next', params=params)

    def set_shuffle(self, state, deviceid=None):

        log.log("setShuffle", state, deviceid)

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self._make_put_request('setShuffle', 'me/player/shuffle', params=params)

    def set_volume(self, volume, deviceid=None):

        log.log("setVolume", volume, deviceid)

        if 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}

            if deviceid is not None:
                params['device_id'] = deviceid

            req = self._make_put_request('setVolume', 'me/player/volume', params=params)

        else:
            log.log("setVolume", volume, "not allowed")

    def make_playlist(self, name, description=None, public=True, collaborative=False):

        log.log("makePlaylist", name, f'description:{description}', f'public:{public}', f'collaborative:{collaborative}')

        headers = {"Content-Type": "application/json"}

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description is not None:
            json["description"] = description

        req = self._make_post_request('makePlaylist', f'users/{self.user.username}/playlists', json=json, headers=headers)

        if req is not None:
            resp = req.json()

            if resp is not None:
                playlist = Playlist(resp["id"], uri=resp['uri'], name=resp['name'], userid=resp['owner']['id'])
                return playlist

        return None

    def replace_playlist_tracks(self, playlistid, uris):

        log.log("replacePlaylistTracks", playlistid)

        headers = {"Content-Type": "application/json"}

        json = {"uris": uris[:100]}

        req = self._make_put_request('replacePlaylistTracks', f'playlists/{playlistid}/tracks', json=json, headers=headers)

        if req is not None:
            resp = req.json()

            if len(uris) > 100:
                self.add_playlist_tracks(playlistid, uris[100:])

    def change_playlist_details(self, playlistid, name=None, public=None, collaborative=None, description=None):

        log.log("changePlaylistDetails", playlistid)

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

        log.log("addPlaylistTracks", playlistid)

        headers = {"Content-Type": "application/json"}

        json = {"uris": uris[:100]}

        req = self._make_post_request('addPlaylistTracks', f'playlists/{playlistid}/tracks', json=json, headers=headers)

        if req is not None:
            resp = req.json()

            if len(uris) > 100:

                self.add_playlist_tracks(playlistid, uris[100:])
