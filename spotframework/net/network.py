import requests
from . import const
from spotframework.model.playlist import playlist as playlistclass

limit = 50


class network:

    def __init__(self, user):
        self.user = user

    def getPlaylist(self, playlistid, tracksonly=False):
        print('getting ' + playlistid)

        tracks = self.getPlaylistTracks(playlistid)

        playlist = playlistclass(playlistid)
        playlist.tracks += tracks

        if not tracksonly:
            pass

        return playlist

    def getPlaylists(self, offset=0):
        print('getting user playlists {}'.format(offset))

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        playlists = []

        params = {'offset': offset, 'limit': limit}
        req = requests.get(const.api_url + 'me/playlists', params=params, headers=headers)

        #print(req.text)

        if req.status_code == 200:

            #print(req.text)

            resp = req.json()

            for responseplaylist in resp['items']:

                playlist = self.getPlaylist(responseplaylist['id'], tracksonly=True)
                playlist.name = responseplaylist['name']
                playlist.userid = responseplaylist['owner']['id']

                playlists.append(playlist)

            #playlists = playlists + resp['items']

            if resp['next']:
                playlists += self.getPlaylists(offset + limit)

            #print(req.text)

            return playlists

        else:
            return None

    def getUserPlaylists(self):

        return list(filter(lambda x: x.userid == self.user.username, self.getPlaylists()))

    def getPlaylistTracks(self, playlistid, offset=0):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        tracks = []

        params = {'offset': offset, 'limit': limit}
        req = requests.get(const.api_url + 'playlists/{}/tracks'.format(playlistid), params=params, headers=headers)

        #print(req.text)

        if req.status_code == 200:

            #print(req.text)
            resp = req.json()

            tracks += resp['items']

            if resp['next']:
                tracks += self.getPlaylistTracks(playlistid, offset + limit)

            #print(req.text)

            return tracks

        else:
            raise ValueError("Couldn't Pull Playlist " + str(playlistid) + ' ' + str(req.status_code))

    def getAvailableDevices(self):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        req = requests.get(const.api_url + 'me/player/devices', headers=headers)

        if req.status_code == 200:
            return req.json()
        else:
            return None

    def getPlayer(self):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        req = requests.get(const.api_url + 'me/player', headers=headers)

        if req.status_code == 200:
            return req.json()
        else:
            return None

    def getDeviceID(self, devicename):

        return next((i for i in self.getAvailableDevices()['devices'] if i['name'] == devicename), None)['id']

    def play(self, uri, deviceid=None):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        payload = {'context_uri': uri}

        req = requests.put(const.api_url + 'me/player/play', params=params, json=payload, headers=headers)

        print(req.status_code)
        print(req.text)

    def next(self, deviceid=None):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = requests.post(const.api_url + 'me/player/next', params=params, headers=headers)

        print(req.status_code)
        print(req.text)

    def setShuffle(self, state, deviceid=None):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = requests.put(const.api_url + 'me/player/shuffle', params=params, headers=headers)

        print(req.status_code)
        print(req.text)

    def setVolume(self, volume, deviceid=None):

        headers = {'Authorization': 'Bearer ' + self.user.access_token}

        params = {'volume_percent': volume}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = requests.put(const.api_url + 'me/player/volume', params=params, headers=headers)

        print(req.status_code)
        print(req.text)
