import requests
from . import const
from spotframework.model.playlist import playlist as playlistclass
import spotframework.log.log as log

limit = 50


class network:

    def __init__(self, user):
        self.user = user

    def _makeGetRequest(self, method, url, params=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        req = requests.get(const.api_url + url, params=params, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'get', str(req.status_code))
            return req.json()
        else:
            log.log(method, 'get', str(req.status_code), req.text)

        return None

    def _makePostRequest(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        req = requests.post(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'post', str(req.status_code))
            return req
        else:
            log.log(method, 'post', str(req.status_code), req.text)

        return None

    def _makePutRequest(self, method, url, params=None, json=None, headers={}):

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        req = requests.put(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            log.log(method, 'put', str(req.status_code))
            return req
        else:
            log.log(method, 'put', str(req.status_code), req.text)

        return None


    def getPlaylist(self, playlistid, tracksonly=False):

        log.log("getPlaylist", playlistid)

        tracks = self.getPlaylistTracks(playlistid)

        playlist = playlistclass(playlistid)
        playlist.tracks += tracks

        if not tracksonly:
            pass

        return playlist

    def getPlaylists(self, offset=0):

        log.log("getPlaylists", offset)

        playlists = []

        params = {'offset': offset, 'limit': limit}

        resp = self._makeGetRequest('getPlaylists', 'me/playlists', params=params)

        if resp:

            for responseplaylist in resp['items']:

                playlist = playlistclass(responseplaylist['id'], responseplaylist['uri'])
                playlist.name = responseplaylist['name']
                playlist.userid = responseplaylist['owner']['id']

                playlists.append(playlist)

            #playlists = playlists + resp['items']

            if resp['next']:
                playlists += self.getPlaylists(offset + limit)

            return playlists

        else:
            return None

    def getUserPlaylists(self):

        log.log("getUserPlaylists")

        return list(filter(lambda x: x.userid == self.user.username, self.getPlaylists()))

    def getPlaylistTracks(self, playlistid, offset=0):

        log.log("getPlaylistTracks", playlistid, offset)

        tracks = []

        params = {'offset': offset, 'limit': limit}

        resp = self._makeGetRequest('getPlaylistTracks', 'playlists/{}/tracks'.format(playlistid), params=params)

        tracks += resp['items']

        if resp['next']:
            tracks += self.getPlaylistTracks(playlistid, offset + limit)

        return tracks


    def getAvailableDevices(self):

        log.log("getAvailableDevices")

        return self._makeGetRequest('getAvailableDevices', 'me/player/devices')


    def getPlayer(self):

        log.log("getPlayer")

        return self._makeGetRequest('getPlayer', 'me/player')


    def getDeviceID(self, devicename):

        log.log("getDeviceID", devicename)

        return next((i for i in self.getAvailableDevices()['devices'] if i['name'] == devicename), None)['id']

    def play(self, uri, deviceid=None):

        log.log("play", uri, deviceid)

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        payload = {'context_uri': uri}

        req = self._makePutRequest('play', 'me/player/play', params=params, json=payload)


    def next(self, deviceid=None):

        log.log("next", deviceid)

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._makePostRequest('next', 'me/player/next', params=params)


    def setShuffle(self, state, deviceid=None):

        log.log("setShuffle", state, deviceid)

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self._makePutRequest('setShuffle', 'me/player/shuffle', params=params)


    def setVolume(self, volume, deviceid=None):

        log.log("setVolume", volume, deviceid)

        if 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}

            if deviceid is not None:
                params['device_id'] = deviceid

            req = self._makePutRequest('setVolume', 'me/player/volume', params=params)

        else:
            log.log("setVolume", volume, "not allowed")

    def makePlaylist(self, name, description=None, public=True, collaborative=False):

        log.log("makePlaylist", name, 'description:{}'.format(description), 'public:{}'.format(public), 'collaborative:{}'.format(collaborative))

        headers = {"Content-Type": "application/json"}

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description is not None:
            json["description"] = description

        resp = self._makePostRequest('makePlaylist', 'users/{}/playlists'.format(self.user.username), json=json, headers=headers).json()

        if resp is not None:

            playlist = playlistclass(resp["id"], uri=resp['uri'], name=resp['name'], userid=resp['owner']['id'])
            return playlist

        return None
