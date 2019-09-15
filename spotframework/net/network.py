import requests
import random
import logging
import time
from typing import List, Optional
from datetime import datetime
from . import const
from spotframework.net.parse import parse
from spotframework.net.user import NetworkUser
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.model.track import Track, PlaylistTrack, PlayedTrack
from spotframework.model.service import CurrentlyPlaying, Device
from spotframework.model.uri import Uri
from requests.models import Response

limit = 50

logger = logging.getLogger(__name__)


class Network:

    def __init__(self, user: NetworkUser):
        self.user = user

    def _make_get_request(self, method, url, params=None, headers={}) -> Optional[dict]:

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.get(const.api_url + url, params=params, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} get {req.status_code}')

            if req.status_code != 204:
                return req.json()
            else:
                return None
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if retry_after:
                    logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                    time.sleep(int(retry_after) + 1)
                    return self._make_get_request(method, url, params, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self._make_get_request(method, url, params, headers)

            else:
                error_text = req.json()['error']['message']
                logger.error(f'{method} get {req.status_code} {error_text}')

        return None

    def _make_post_request(self, method, url, params=None, json=None, headers={}) -> Optional[Response]:

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.post(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} post {req.status_code}')
            return req
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if retry_after:
                    logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                    time.sleep(int(retry_after) + 1)
                    return self._make_post_request(method, url, params, json, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self._make_post_request(method, url, params, json, headers)

            else:
                error_text = str(req.text)
                logger.error(f'{method} post {req.status_code} {error_text}')

        return None

    def _make_put_request(self, method, url, params=None, json=None, headers={}) -> Optional[Response]:

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        req = requests.put(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} put {req.status_code}')
            return req
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if retry_after:
                    logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                    time.sleep(int(retry_after) + 1)
                    return self._make_put_request(method, url, params, json, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self._make_put_request(method, url, params, json, headers)

            else:
                error_text = str(req.text)
                logger.error(f'{method} put {req.status_code} {error_text}')

        return None

    def get_playlist(self, uri: Uri) -> Optional[SpotifyPlaylist]:

        logger.info(f"{uri}")

        tracks = self.get_playlist_tracks(uri)

        if tracks is not None:

            playlist = SpotifyPlaylist(uri.object_id)
            playlist.tracks += tracks

            return playlist
        else:
            logger.error(f"{uri} - no tracks returned")
            return None

    def create_playlist(self,
                        username,
                        name='New Playlist',
                        public=True,
                        collaborative=False,
                        description=None) -> Optional[SpotifyPlaylist]:

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description:
            json['description'] = description

        req = self._make_post_request('createPlaylist', f'users/{username}/playlists', json=json)

        if 200 <= req.status_code < 300:
            return parse.parse_playlist(req.json())
        else:
            logger.error('error creating playlist')
            return None

    def get_playlists(self, offset=0) -> Optional[List[SpotifyPlaylist]]:

        logger.info(f"{offset}")

        playlists = []

        params = {'offset': offset, 'limit': limit}

        resp = self._make_get_request('getPlaylists', 'me/playlists', params=params)

        if resp:

            for responseplaylist in resp['items']:
                playlists.append(parse.parse_playlist(responseplaylist))

            if resp.get('next', None):
                more_playlists = self.get_playlists(offset + limit)
                if more_playlists:
                    playlists += more_playlists

            return playlists

        else:
            logger.error(f'error getting playlists offset={offset}')
            return None

    def get_user_playlists(self) -> Optional[List[SpotifyPlaylist]]:

        logger.info('retrieved')

        playlists = self.get_playlists()

        if playlists:
            return list(filter(lambda x: x.owner.username == self.user.username, playlists))
        else:
            logger.error('no playlists returned to filter')
            return None

    def get_playlist_tracks(self, uri: Uri, offset=0) -> List[PlaylistTrack]:

        logger.info(f"{uri}{' ' + str(offset) if offset is not 0 else ''}")

        tracks = []

        params = {'offset': offset, 'limit': limit}

        resp = self._make_get_request('getPlaylistTracks', f'playlists/{uri.object_id}/tracks', params=params)

        if resp:
            if resp.get('items', None):
                tracks += [parse.parse_track(i) for i in resp.get('items', None)]
            else:
                logger.warning(f'{uri} no items returned')

            if resp.get('next', None):
                more_tracks = self.get_playlist_tracks(uri, offset + limit)
                if more_tracks:
                    tracks += more_tracks
        else:
            logger.warning(f'{uri} error on response')

        return tracks

    def get_available_devices(self) -> Optional[List[Device]]:

        logger.info("retrieving")

        resp = self._make_get_request('getAvailableDevices', 'me/player/devices')
        if resp:
            return [parse.parse_device(i) for i in resp['devices']]
        else:
            logger.error('no devices returned')
            return None

    def get_recently_played_tracks(self,
                                   response_limit: int = None,
                                   after: datetime = None,
                                   before: datetime = None) -> Optional[List[PlayedTrack]]:

        logger.info("retrieving")

        params = dict()

        if response_limit:
            params['limit'] = response_limit
        if after and before:
            raise ValueError('cant have before and after')
        if after:
            params['after'] = int(after.timestamp() * 1000)
        if before:
            params['before'] = int(before.timestamp() * 1000)

        resp = self._make_get_request('getRecentlyPlayedTracks', 'me/player/recently-played', params=params)

        if resp:
            return [parse.parse_track(i) for i in resp['items']]
        else:
            logger.error('no tracks returned')
            return None

    def get_player(self) -> Optional[CurrentlyPlaying]:

        logger.info("retrieved")

        resp = self._make_get_request('getPlayer', 'me/player')
        if resp:
            return parse.parse_currently_playing(resp)
        else:
            logger.info('no player returned')
            return None

    def get_device_id(self, devicename) -> Optional[str]:

        logger.info(f"{devicename}")

        devices = self.get_available_devices()
        if devices:
            device = next((i for i in devices if i.name == devicename), None)
            if device:
                return device.device_id
            else:
                logger.error(f'{devicename} not found')
        else:
            logger.error('no devices returned')

    def change_playback_device(self, device_id):

        logger.info(device_id)

        json = {
            'device_ids': [device_id],
            'play': True
        }

        resp = self._make_put_request('changePlaybackDevice', 'me/player', json=json)
        if resp:
            return True
        else:
            return None

    def play(self, uri: Uri = None, uris: List[Uri] = None, deviceid=None) -> Optional[Response]:

        logger.info(f"{uri}{' ' + deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        if uri and uris:
            raise Exception('wont take both context uri and uris')

        payload = dict()

        if uri:
            payload['context_uri'] = str(uri)
        if uris:
            payload['uris'] = [str(i) for i in uris[:200]]

        req = self._make_put_request('play', 'me/player/play', params=params, json=payload)
        if req:
            return req
        else:
            logger.error('error playing')

    def pause(self, deviceid=None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_put_request('pause', 'me/player/pause', params=params)
        if req:
            return req
        else:
            logger.error('error pausing')

    def next(self, deviceid=None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_post_request('next', 'me/player/next', params=params)
        if req:
            return req
        else:
            logger.error('error skipping')

    def previous(self, deviceid=None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self._make_post_request('previous', 'me/player/previous', params=params)
        if req:
            return req
        else:
            logger.error('error reversing')

    def set_shuffle(self, state, deviceid=None) -> Optional[Response]:

        logger.info(f"{state}{' ' + deviceid if deviceid is not None else ''}")

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self._make_put_request('setShuffle', 'me/player/shuffle', params=params)
        if req:
            return req
        else:
            logger.error(f'error setting shuffle {state}')

    def set_volume(self, volume, deviceid=None) -> Optional[Response]:

        logger.info(f"{volume}{' ' + deviceid if deviceid is not None else ''}")

        if volume.isdigit() and 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}

            if deviceid is not None:
                params['device_id'] = deviceid

            req = self._make_put_request('setVolume', 'me/player/volume', params=params)
            if req:
                return req
            else:
                logger.error(f'error setting volume {volume}')
                return None

        else:
            logger.error(f"{volume} not accepted value")
            return None

    def replace_playlist_tracks(self, uri: Uri, uris: List[Uri]):

        logger.info(f"{uri}")

        headers = {"Content-Type": "application/json"}

        json = {"uris": [str(i) for i in uris[:100]]}

        req = self._make_put_request('replacePlaylistTracks', f'playlists/{uri.object_id}/tracks',
                                     json=json, headers=headers)

        if req is not None:

            if len(uris) > 100:
                return self.add_playlist_tracks(uri, uris[100:])

            return req
        else:
            logger.error(f'error replacing playlist tracks, total: {len(uris)}')

    def change_playlist_details(self,
                                uri: Uri,
                                name=None,
                                public=None,
                                collaborative=None,
                                description=None) -> Optional[Response]:

        logger.info(f"{uri}")

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

        if len(json) == 0:
            logger.warning('update dictionairy length 0')
            return None
        else:
            req = self._make_put_request('changePlaylistDetails', f'playlists/{uri.object_id}',
                                         json=json, headers=headers)
            if req:
                return req
            else:
                logger.error('error updating details')
                return None

    def add_playlist_tracks(self, uri: Uri, uris: List[Uri]) -> List[dict]:

        logger.info(f"{uri}")

        headers = {"Content-Type": "application/json"}

        json = {"uris": [str(i) for i in uris[:100]]}

        req = self._make_post_request('addPlaylistTracks', f'playlists/{uri.object_id}/tracks',
                                      json=json, headers=headers)

        if req is not None:
            resp = req.json()

            snapshots = [resp]

            if len(uris) > 100:

                snapshots += self.add_playlist_tracks(uri, uris[100:])

            return snapshots

        else:
            logger.error(f'error retrieving tracks {uri}, total: {len(uris)}')
            return []

    def get_recommendations(self, tracks=None, artists=None, response_limit=10) -> Optional[List[Track]]:

        logger.info(f'sample size: {response_limit}')

        params = {'limit': response_limit}

        if tracks:
            random.shuffle(tracks)
            params['seed_tracks'] = tracks[:100]
        if artists:
            random.shuffle(artists)
            params['seed_artists'] = artists[:100]

        if len(params) == 1:
            logger.warning('update dictionairy length 0')
            return None
        else:
            resp = self._make_get_request('getRecommendations', 'recommendations', params=params)
            if resp:
                if 'tracks' in resp:
                    return [parse.parse_track(i) for i in resp['tracks']]
                else:
                    logger.error('no tracks returned')
                    return None
            else:
                logger.error('error getting recommendations')
                return None

    def write_playlist_object(self,
                              playlist: SpotifyPlaylist,
                              append_tracks: bool = False):

        if playlist.uri:
            if playlist.tracks == -1:
                self.replace_playlist_tracks(playlist.uri, [])
            elif playlist.tracks:
                if append_tracks:
                    self.add_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks])
                else:
                    self.replace_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks])

            if playlist.name or playlist.collaborative or playlist.public or playlist.description:
                self.change_playlist_details(playlist.uri,
                                             playlist.name,
                                             playlist.public,
                                             playlist.collaborative,
                                             playlist.description)

        else:
            logger.error('playlist has no id')

    def reorder_playlist_tracks(self,
                                uri: Uri,
                                range_start: int,
                                range_length: int,
                                insert_before: int) -> Optional[Response]:

        logger.info(f'id: {uri}')

        if range_start < 0:
            logger.error('range_start must be positive')
            raise ValueError('range_start must be positive')
        if range_length < 0:
            logger.error('range_length must be positive')
            raise ValueError('range_length must be positive')
        if insert_before < 0:
            logger.error('insert_before must be positive')
            raise ValueError('insert_before must be positive')

        json = {'range_start': range_start,
                'range_length': range_length,
                'insert_before': insert_before}

        resp = self._make_put_request('reorderPlaylistTracks', f'playlists/{uri.object_id}/tracks', json=json)

        if resp:
            return resp
        else:
            logger.error('error reordering playlist')
