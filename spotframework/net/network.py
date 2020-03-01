import requests
import random
import logging
import time
from typing import List, Optional, Union
import datetime

from spotframework.model.artist import SpotifyArtist
from spotframework.model.user import User
from . import const
from spotframework.net.user import NetworkUser
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.model.track import Track, SpotifyTrack, PlaylistTrack, PlayedTrack, LibraryTrack, AudioFeatures
from spotframework.model.album import LibraryAlbum, SpotifyAlbum
from spotframework.model.service import CurrentlyPlaying, Device, Context
from spotframework.model.uri import Uri
from requests.models import Response

limit = 50

logger = logging.getLogger(__name__)


class SearchResponse:
    def __init__(self,
                 tracks: List[SpotifyTrack],
                 albums: List[SpotifyAlbum],
                 artists: List[SpotifyArtist],
                 playlists: List[SpotifyPlaylist]):
        self.tracks = tracks
        self.albums = albums
        self.artists = artists
        self.playlists = playlists

    @property
    def all(self):
        return self.tracks + self.albums + self.artists + self.playlists


class Network:
    """Network layer class for reading and manipulating spotify service"""

    def __init__(self, user: NetworkUser):
        """Create network using NetworkUser containing credentials

        :param user: target spotify user
        """
        self.user = user
        self.refresh_counter = 0

    def get_request(self, method, url=None, params=None, headers=None, whole_url=None) -> Optional[dict]:
        """HTTP get request for reading from service

        :param method: spotify api method for logging
        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param headers: additional request headers
        :param whole_url: override base api url with new hostname and url
        :return: dictionary of json response if available
        """

        if headers is None:
            headers = dict()

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        if whole_url:
            req = requests.get(whole_url, params=params, headers=headers)
        else:
            req = requests.get(const.api_url + url, params=params, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} get {url if whole_url is not None else whole_url} {req.status_code}')

            if req.status_code != 204:
                return req.json()
            else:
                return None
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    if retry_after:
                        logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                        time.sleep(int(retry_after) + 1)
                        return self.get_request(method, url, params, headers)
                    else:
                        logger.error(f'{method} rate limit reached: cannot find Retry-After header')
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    return self.get_request(method, url, params, headers)
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            else:
                error = req.json().get('error', None)
                if error:
                    message = error.get('message', 'n/a')
                    logger.error(f'{method} {req.status_code} {message}')
                else:
                    logger.error(f'{method} {req.status_code} no error object found')

        return None

    def post_request(self, method, url, params=None, json=None, headers=None) -> Optional[Response]:
        """HTTP post request for reading from service

        :param method: spotify api method for logging
        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param json: dictionary request body for conversion to json during transmission
        :param headers: additional request headers
        :return: response object if available
        """

        if headers is None:
            headers = dict()

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        req = requests.post(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} post {url} {req.status_code}')
            return req
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    if retry_after:
                        logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                        time.sleep(int(retry_after) + 1)
                        return self.post_request(method, url, params, json, headers)
                    else:
                        logger.error(f'{method} rate limit reached: cannot find Retry-After header')
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    return self.post_request(method, url, params, json, headers)
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            else:
                error = req.json().get('error', None)
                if error:
                    message = error.get('message', 'n/a')
                    logger.error(f'{method} {req.status_code} {message}')
                else:
                    logger.error(f'{method} {req.status_code} no error object found')

        return None

    def put_request(self, method, url, params=None, json=None, headers=None) -> Optional[Response]:
        """HTTP put request for reading from service

        :param method: spotify api method for logging
        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param json: dictionary request body for conversion to json during transmission
        :param headers: additional request headers
        :return: response object if available
        """

        if headers is None:
            headers = dict()

        headers['Authorization'] = 'Bearer ' + self.user.access_token

        req = requests.put(const.api_url + url, params=params, json=json, headers=headers)

        if 200 <= req.status_code < 300:
            logger.debug(f'{method} put {url} {req.status_code}')
            return req
        else:

            if req.status_code == 429:
                retry_after = req.headers.get('Retry-After', None)

                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    if retry_after:
                        logger.warning(f'{method} rate limit reached: retrying in {retry_after} seconds')
                        time.sleep(int(retry_after) + 1)
                        return self.put_request(method, url, params, json, headers)
                    else:
                        logger.error(f'{method} rate limit reached: cannot find Retry-After header')
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    return self.put_request(method, url, params, json, headers)
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} refresh token limit (5) reached')

            else:
                error = req.json().get('error', None)
                if error:
                    message = error.get('message', 'n/a')
                    logger.error(f'{method} {req.status_code} {message}')
                else:
                    logger.error(f'{method} {req.status_code} no error object found')

        return None

    def get_playlist(self,
                     uri: Uri = None,
                     uri_string: str = None,
                     tracks: bool = True) -> Optional[SpotifyPlaylist]:
        """get playlist object with tracks for uri

        :param uri: target request uri
        :param uri_string: target request uri as string
        :param tracks: populate tracks of playlist during generation
        :return: playlist object
        """

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        logger.info(f"retrieving {uri}")

        resp = self.get_request('getPlaylist', f'playlists/{uri.object_id}')

        if resp:
            playlist = self.parse_playlist(resp)

            if tracks and resp.get('tracks'):
                if 'next' in resp['tracks']:
                    logger.debug(f'paging tracks for {uri}')

                    track_pager = PageCollection(net=self, page=resp['tracks'])
                    track_pager.continue_iteration()

                    playlist.tracks = [self.parse_track(i) for i in track_pager.items]
                else:
                    logger.debug(f'parsing {len(resp.get("tracks"))} tracks for {uri}')
                    playlist.tracks = [self.parse_track(i) for i in resp.get('tracks', [])]

            return playlist
        else:
            logger.error('no playlist returned')
            return None

    def create_playlist(self,
                        username: str,
                        name: str = 'New Playlist',
                        public: bool = True,
                        collaborative: bool = False,
                        description: bool = None) -> Optional[SpotifyPlaylist]:
        """create playlist for user

        :param username: username for playlist creation
        :param name: new playlist name
        :param public: make playlist public
        :param collaborative: make playlist collaborative
        :param description: description for new playlist
        :return: newly created playlist object
        """
        logger.info(f'creating {name} for {username}, '
                    f'public: {public}, collaborative: {collaborative}, description: {description}')

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description:
            json['description'] = description

        req = self.post_request('createPlaylist', f'users/{username}/playlists', json=json)

        if 200 <= req.status_code < 300:
            return self.parse_playlist(req.json())
        else:
            logger.error('error creating playlist')
            return None

    def get_playlists(self, response_limit: int = None) -> Optional[List[SpotifyPlaylist]]:
        """get current users playlists

        :param response_limit: max playlists to return
        :return: List of user created and followed playlists if available
        """

        logger.info(f"paging playlists")

        pager = PageCollection(net=self, url='me/playlists', name='getPlaylists')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_playlist(i) for i in pager.items]

        if len(return_items) == 0:
            logger.error('no playlists returned')

        return return_items

    def get_library_albums(self, response_limit: int = None) -> Optional[List[LibraryAlbum]]:
        """get user library albums

        :param response_limit: max albums to return
        :return: List of user library albums if available
        """

        logger.info(f"paging library albums")

        pager = PageCollection(net=self, url='me/albums', name='getLibraryAlbums')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_album(i) for i in pager.items]

        if len(return_items) == 0:
            logger.error('no albums returned')

        return return_items

    def get_library_tracks(self, response_limit: int = None) -> Optional[List[LibraryTrack]]:
        """get user library tracks

        :param response_limit: max tracks to return
        :return: List of saved library trakcs if available
        """

        logger.info(f"paging library tracks")

        pager = PageCollection(net=self, url='me/tracks', name='getLibraryTracks')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_track(i) for i in pager.items]

        if len(return_items) == 0:
            logger.error('no tracks returned')

        return return_items

    def get_user_playlists(self) -> Optional[List[SpotifyPlaylist]]:
        """retrieve user owned playlists

        :return: List of user owned playlists if available
        """

        logger.info('pulling all playlists')

        playlists = self.get_playlists()

        if self.user.username is None:
            logger.debug('no user info, refreshing for filter')
            self.user.refresh_info()

        if playlists is not None:
            return list(filter(lambda x: x.owner.username == self.user.username, playlists))
        else:
            logger.error('no playlists returned to filter')

    def get_playlist_tracks(self,
                            uri: Uri = None,
                            uri_string: str = None,
                            response_limit: int = None) -> List[PlaylistTrack]:
        """get list of playlists tracks for uri

        :param uri: target playlist uri
        :param uri_string: target playlist uri as string
        :param response_limit: max tracks to return
        :return: list of playlist tracks if available
        """

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        logger.info(f"paging tracks for {uri}")

        pager = PageCollection(net=self, url=f'playlists/{uri.object_id}/tracks', name='getPlaylistTracks')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_track(i) for i in pager.items]

        if len(return_items) == 0:
            logger.error('no tracks returned')

        return return_items

    def get_available_devices(self) -> Optional[List[Device]]:
        """get users available devices"""

        logger.info("polling available devices")

        resp = self.get_request('getAvailableDevices', 'me/player/devices')
        if resp:
            if len(resp['devices']) == 0:
                logger.error('no devices returned')
            return [self.parse_device(i) for i in resp['devices']]
        else:
            logger.error('no devices returned')
            return None

    def get_recently_played_tracks(self,
                                   response_limit: int = None,
                                   after: datetime.datetime = None,
                                   before: datetime.datetime = None) -> Optional[List[PlayedTrack]]:
        """get list of recently played tracks

        :param response_limit: max number of tracks to return
        :param after: datetime after which to return tracks
        :param before: datetime before which to return tracks
        :return: list of recently played tracks if available
        """

        logger.info(f"paging {'all' if response_limit is None else response_limit} recent tracks ({after}/{before})")

        params = dict()
        if after and before:
            raise ValueError('cant have before and after')
        if after:
            params['after'] = int(after.timestamp() * 1000)
        if before:
            params['before'] = int(before.timestamp() * 1000)

        resp = self.get_request('getRecentlyPlayedTracks', 'me/player/recently-played', params=params)

        if resp:
            pager = PageCollection(self, page=resp)
            if response_limit:
                pager.total_limit = response_limit
            else:
                pager.total_limit = 20
            pager.continue_iteration()

            return [self.parse_track(i) for i in pager.items]
        else:
            logger.error('no tracks returned')

    def get_player(self) -> Optional[CurrentlyPlaying]:
        """get currently playing snapshot (player)"""

        logger.info("polling player")

        resp = self.get_request('getPlayer', 'me/player')
        if resp:
            return self.parse_currently_playing(resp)
        else:
            logger.info('no player returned')

    def get_device_id(self, device_name: str) -> Optional[str]:
        """return device id of device as searched for by name

        :param device_name: target device name
        :return: device ID
        """

        logger.info(f"querying {device_name}")

        devices = self.get_available_devices()
        if devices:
            device = next((i for i in devices if i.name == device_name), None)
            if device:
                return device.device_id
            else:
                logger.error(f'{device_name} not found')
        else:
            logger.error('no devices returned')

    def change_playback_device(self, device_id: str):
        """migrate playback to different device"""

        logger.info(device_id)

        json = {
            'device_ids': [device_id],
            'play': True
        }

        logger.info(f'shifting playback to {device_id}')

        resp = self.put_request('changePlaybackDevice', 'me/player', json=json)
        if resp:
            return True
        else:
            return None

    def play(self,
             uri: Uri = None,
             uri_string: str = None,
             uris: List[Uri] = None,
             uri_strings: List[str] = None,
             deviceid: str = None) -> Optional[Response]:
        """begin playback"""

        if uri_string is not None:
            uri = Uri(uri_string)

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

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

        req = self.put_request('play', 'me/player/play', params=params, json=payload)
        if req:
            return req
        else:
            logger.error('error playing')

    def pause(self, deviceid: str = None) -> Optional[Response]:
        """pause playback"""

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.put_request('pause', 'me/player/pause', params=params)
        if req:
            return req
        else:
            logger.error('error pausing')

    def next(self, deviceid: str = None) -> Optional[Response]:
        """skip track playback"""

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.post_request('next', 'me/player/next', params=params)
        if req:
            return req
        else:
            logger.error('error skipping')

    def previous(self, deviceid: str = None) -> Optional[Response]:
        """skip playback backwards"""

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.post_request('previous', 'me/player/previous', params=params)
        if req:
            return req
        else:
            logger.error('error reversing')

    def set_shuffle(self, state: bool, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{state}{' ' + deviceid if deviceid is not None else ''}")

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self.put_request('setShuffle', 'me/player/shuffle', params=params)
        if req:
            return req
        else:
            logger.error(f'error setting shuffle {state}')

    def set_volume(self, volume: int, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{volume}{' ' + deviceid if deviceid is not None else ''}")

        if 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}

            if deviceid is not None:
                params['device_id'] = deviceid

            req = self.put_request('setVolume', 'me/player/volume', params=params)
            if req:
                return req
            else:
                logger.error(f'error setting volume {volume}')
                return None

        else:
            logger.error(f"{volume} not accepted value")
            return None

    def replace_playlist_tracks(self,
                                uri: Uri = None,
                                uri_string: str = None,
                                uris: List[Uri] = None,
                                uri_strings: List[str] = None):

        if uri_string is not None:
            uri = Uri(uri_string)

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

        logger.info(f"replacing {uri} with {'0' if uris is None else len(uris)} tracks")

        headers = {"Content-Type": "application/json"}

        json = {"uris": [str(i) for i in uris[:100]]}

        req = self.put_request('replacePlaylistTracks', f'playlists/{uri.object_id}/tracks',
                               json=json, headers=headers)

        if req is not None:

            if len(uris) > 100:
                return self.add_playlist_tracks(uri, uris[100:])

            return req
        else:
            logger.error(f'error replacing playlist tracks, total: {len(uris)}')

    def change_playlist_details(self,
                                uri: Uri,
                                name: str = None,
                                public: bool = None,
                                collaborative: bool = None,
                                description: str = None) -> Optional[Response]:

        logger.info(f"updating {uri}, name: {name}, public: {public}, collab: {collaborative}, "
                    f"description: {(description[:30] + '...' if len(description) > 33 else description) if description is not None else None}")

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
            req = self.put_request('changePlaylistDetails', f'playlists/{uri.object_id}',
                                   json=json, headers=headers)
            if req:
                return req
            else:
                logger.error('error updating details')
                return None

    def add_playlist_tracks(self, uri: Uri, uris: List[Uri]) -> List[dict]:

        logger.info(f"adding {len(uris)} tracks to {uri}")

        headers = {"Content-Type": "application/json"}

        json = {"uris": [str(i) for i in uris[:100]]}

        req = self.post_request('addPlaylistTracks', f'playlists/{uri.object_id}/tracks',
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

    def get_recommendations(self,
                            tracks: List[Track] = None,
                            artists: List[SpotifyArtist] = None,
                            response_limit=10) -> Optional[List[Track]]:

        logger.info(f'getting {response_limit} recommendations, '
                    f'tracks: {len(tracks) if tracks is not None else 0}, '
                    f'artists: {len(artists) if artists is not None else 0}')

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
            resp = self.get_request('getRecommendations', 'recommendations', params=params)
            if resp:
                if 'tracks' in resp:
                    return [self.parse_track(i) for i in resp['tracks']]
                else:
                    logger.error('no tracks returned')
                    return None
            else:
                logger.error('error getting recommendations')
                return None

    def write_playlist_object(self,
                              playlist: SpotifyPlaylist,
                              append_tracks: bool = False):
        logger.info(f'writing {playlist.name}, append tracks: {append_tracks}')

        if playlist.uri:
            if playlist.tracks == -1:
                logger.debug(f'wiping {playlist.name} tracks')
                self.replace_playlist_tracks(uri=playlist.uri, uris=[])
            elif playlist.tracks:
                if append_tracks:
                    self.add_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks if
                                                            isinstance(i, SpotifyTrack)])
                else:
                    self.replace_playlist_tracks(uri=playlist.uri, uris=[i.uri for i in playlist.tracks if
                                                                         isinstance(i, SpotifyTrack)])

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

        logger.info(f'reordering {uri} tracks, start: {range_start}, length: {range_length}, before: {insert_before}')

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

        resp = self.put_request('reorderPlaylistTracks', f'playlists/{uri.object_id}/tracks', json=json)

        if resp:
            return resp
        else:
            logger.error('error reordering playlist')

    def get_track_audio_features(self, uris: List[Uri]):
        logger.info(f'getting {len(uris)} features')

        audio_features = []
        chunked_uris = list(self.chunk(uris, 100))
        for chunk in chunked_uris:
            resp = self.get_request('getAudioFeatures',
                                    url='audio-features',
                                    params={'ids': ','.join(i.object_id for i in chunk)})

            if resp:
                if resp.get('audio_features', None):

                    for feature in resp['audio_features']:
                        if feature is not None:
                            audio_features.append(self.parse_audio_features(feature))
                        else:
                            audio_features.append(None)

                else:
                    logger.error('no audio features included')
            else:
                logger.error('no response')

        if len(audio_features) == len(uris):
            return audio_features
        else:
            logger.error('mismatched length of input and response')

    def populate_track_audio_features(self, tracks=Union[SpotifyTrack, List[SpotifyTrack]]):
        logger.info(f'populating {len(tracks)} features')

        if isinstance(tracks, SpotifyTrack):
            audio_features = self.get_track_audio_features([tracks.uri])

            if audio_features:
                if len(audio_features) == 1:
                    tracks.audio_features = audio_features[0]
                    return tracks
                else:
                    logger.error(f'{len(audio_features)} features returned')
            else:
                logger.error(f'no audio features returned for {tracks.uri}')

        elif isinstance(tracks, List):
            if all(isinstance(i, SpotifyTrack) for i in tracks):
                audio_features = self.get_track_audio_features([i.uri for i in tracks])

                if audio_features:
                    if len(audio_features) != len(tracks):
                        logger.error(f'{len(audio_features)} features returned for {len(tracks)} tracks')

                    for index, track in enumerate(tracks):
                        track.audio_features = audio_features[index]

                    return tracks
                else:
                    logger.error(f'no audio features returned')
        else:
            raise TypeError('must provide either single or list of spotify tracks')

    def get_tracks(self,
                   uris: List[Uri] = None,
                   uri_strings: List[str] = None) -> List[SpotifyTrack]:

        if uris is None and uri_strings is None:
            raise NameError('no uris provided')

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

        logger.info(f'getting {len(uris)} tracks')

        if not all(i.object_type == Uri.ObjectType.track for i in uris):
            raise TypeError('uris must be of type track')

        tracks = []
        chunked_uris = list(self.chunk(uris, 50))
        for chunk in chunked_uris:
            resp = self.get_request(method='getTracks', url='tracks', params={'ids': ','.join([i.object_id for i in chunk])})
            if resp:
                tracks += [self.parse_track(i) for i in resp.get('tracks', [])]

        return tracks

    def get_track(self, uri: Uri = None, uri_string: str = None) -> Optional[SpotifyTrack]:

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        track = self.get_tracks([uri])
        if len(track) == 1:
            return track[0]
        else:
            return None

    def get_albums(self, uris: List[Uri] = None, uri_strings: List[str] = None) -> List[SpotifyAlbum]:

        if uris is None and uri_strings is None:
            raise NameError('no uris provided')

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

        logger.info(f'getting {len(uris)} albums')

        if not all(i.object_type == Uri.ObjectType.album for i in uris):
            raise TypeError('uris must be of type album')

        albums = []
        chunked_uris = list(self.chunk(uris, 50))
        for chunk in chunked_uris:
            resp = self.get_request(method='getAlbums', url='albums', params={'ids': ','.join([i.object_id for i in chunk])})
            if resp:
                albums += [self.parse_album(i) for i in resp.get('albums', [])]

        return albums

    def get_album(self, uri: Uri = None, uri_string: str = None) -> Optional[SpotifyAlbum]:

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        album = self.get_albums([uri])
        if len(album) == 1:
            return album[0]
        else:
            return None

    def get_artists(self, uris: List[Uri] = None, uri_strings: List[str] = None) -> List[SpotifyArtist]:

        if uris is None and uri_strings is None:
            raise NameError('no uris provided')

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

        logger.info(f'getting {len(uris)} artists')

        if not all(i.object_type == Uri.ObjectType.artist for i in uris):
            raise TypeError('uris must be of type artist')

        artists = []
        chunked_uris = list(self.chunk(uris, 50))
        for chunk in chunked_uris:
            resp = self.get_request(method='getArtists', url='artists', params={'ids': ','.join([i.object_id for i in chunk])})
            if resp:
                artists += [self.parse_artist(i) for i in resp.get('artists', [])]

        return artists

    def get_artist(self, uri: Uri = None, uri_string: str = None) -> Optional[SpotifyArtist]:

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        artist = self.get_artists([uri])
        if len(artist) == 1:
            return artist[0]
        else:
            return None

    def search(self,
               query_types: List[Uri.ObjectType],
               query: str = None,
               track: str = None,
               album: str = None,
               artist: str = None,
               response_limit: int = 20) -> SearchResponse:

        if query is None and track is None and album is None and artist is None:
            raise ValueError('no query parameters')

        queries = []

        if query is not None:
            queries.append(query)
        if track is not None:
            queries.append(f'track:{track}')
        if album is not None:
            queries.append(f'album:{album}')
        if artist is not None:
            queries.append(f'artist:{artist}')

        params = {
            'q': ' '.join(queries),
            'type': ','.join([i.name for i in query_types]),
            'limit': response_limit
        }

        logger.info(f'querying track: {track}, album: {album}, artist: {artist}')

        resp = self.get_request(method='search', url='search', params=params)

        albums = [self.parse_album(i) for i in resp.get('albums', {}).get('items', [])]
        artists = [self.parse_artist(i) for i in resp.get('artists', {}).get('items', [])]
        tracks = [self.parse_track(i) for i in resp.get('tracks', {}).get('items', [])]
        playlists = [self.parse_playlist(i) for i in resp.get('playlists', {}).get('items', [])]

        return SearchResponse(tracks=tracks, albums=albums, artists=artists, playlists=playlists)

    @staticmethod
    def parse_artist(artist_dict) -> SpotifyArtist:

        name = artist_dict.get('name', None)

        href = artist_dict.get('href', None)
        uri = artist_dict.get('uri', None)

        genres = artist_dict.get('genres', None)
        popularity = artist_dict.get('popularity', None)

        if name is None:
            raise KeyError('artist name not found')

        return SpotifyArtist(name,
                             href=href,
                             uri=uri,

                             genres=genres,
                             popularity=popularity)

    def parse_album(self, album_dict) -> Union[SpotifyAlbum, LibraryAlbum]:
        if 'album' in album_dict:
            album = album_dict.get('album', None)
        else:
            album = album_dict

        name = album.get('name', None)
        if name is None:
            raise KeyError('album name not found')

        artists = [self.parse_artist(i) for i in album.get('artists', [])]

        if album.get("album_type") is not None:
            album_type = SpotifyAlbum.Type[album.get('album_type').lower()]
        else:
            album_type = SpotifyAlbum.Type.single

        href = album.get('href', None)
        uri = album.get('uri', None)

        genres = album.get('genres', None)
        if album.get('tracks'):
            if 'next' in album['tracks']:

                track_pager = PageCollection(net=self, page=album['tracks'])
                track_pager.continue_iteration()

                tracks = [self.parse_track(i) for i in track_pager.items]
            else:
                tracks = [self.parse_track(i) for i in album.get('tracks', [])]
        else:
            tracks = []

        release_date = album.get('release_date', None)
        release_date_precision = album.get('release_date_precision', None)

        label = album.get('label', None)
        popularity = album.get('popularity', None)

        added_at = album_dict.get('added_at', None)
        if added_at:
            added_at = datetime.datetime.strptime(added_at, '%Y-%m-%dT%H:%M:%S%z')

        if added_at:
            return LibraryAlbum(name=name,
                                artists=artists,

                                album_type=album_type,

                                href=href,
                                uri=uri,

                                genres=genres,
                                tracks=tracks,

                                release_date=release_date,
                                release_date_precision=release_date_precision,

                                label=label,
                                popularity=popularity,

                                added_at=added_at)
        else:
            return SpotifyAlbum(name=name,
                                artists=artists,

                                album_type=album_type,

                                href=href,
                                uri=uri,

                                genres=genres,
                                tracks=tracks,

                                release_date=release_date,
                                release_date_precision=release_date_precision,

                                label=label,
                                popularity=popularity)

    def parse_track(self, track_dict) -> Union[Track, SpotifyTrack, PlaylistTrack, PlayedTrack, LibraryTrack]:

        if 'track' in track_dict:
            track = track_dict.get('track', None)
        else:
            track = track_dict

        name = track.get('name', None)
        if name is None:
            raise KeyError('track name not found')

        if track.get('album', None):
            album = self.parse_album(track['album'])
        else:
            album = None

        artists = [self.parse_artist(i) for i in track.get('artists', [])]

        href = track.get('href', None)
        uri = track.get('uri', None)

        disc_number = track.get('disc_number', None)
        track_number = track.get('track_number', None)
        duration_ms = track.get('duration_ms', None)
        explicit = track.get('explicit', None)
        is_playable = track.get('is_playable', None)

        popularity = track.get('popularity', None)

        added_by = self.parse_user(track_dict.get('added_by')) if track_dict.get('added_by', None) else None
        added_at = track_dict.get('added_at', None)
        if added_at:
            added_at = datetime.datetime.strptime(added_at, '%Y-%m-%dT%H:%M:%S%z')
        is_local = track_dict.get('is_local', None)

        played_at = track_dict.get('played_at', None)
        if played_at:
            played_at = datetime.datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%f%z')
        context = track_dict.get('context', None)
        if context:
            context = self.parse_context(context)

        if added_by or is_local:
            return PlaylistTrack(name=name,
                                 album=album,
                                 artists=artists,

                                 added_at=added_at,
                                 added_by=added_by,
                                 is_local=is_local,

                                 href=href,
                                 uri=uri,

                                 disc_number=disc_number,
                                 track_number=track_number,
                                 duration_ms=duration_ms,
                                 explicit=explicit,
                                 is_playable=is_playable,

                                 popularity=popularity)
        elif added_at:
            return LibraryTrack(name=name,
                                album=album,
                                artists=artists,

                                href=href,
                                uri=uri,

                                disc_number=disc_number,
                                track_number=track_number,
                                duration_ms=duration_ms,
                                explicit=explicit,
                                is_playable=is_playable,

                                popularity=popularity,
                                added_at=added_at)
        elif played_at or context:
            return PlayedTrack(name=name,
                               album=album,
                               artists=artists,

                               href=href,
                               uri=uri,

                               disc_number=disc_number,
                               track_number=track_number,
                               duration_ms=duration_ms,
                               explicit=explicit,
                               is_playable=is_playable,

                               popularity=popularity,
                               played_at=played_at,
                               context=context)
        else:
            return SpotifyTrack(name=name,
                                album=album,
                                artists=artists,

                                href=href,
                                uri=uri,

                                disc_number=disc_number,
                                track_number=track_number,
                                duration_ms=duration_ms,
                                explicit=explicit,
                                is_playable=is_playable,

                                popularity=popularity)

    @staticmethod
    def parse_user(user_dict) -> User:
        display_name = user_dict.get('display_name', None)

        spotify_id = user_dict.get('id', None)
        href = user_dict.get('href', None)
        uri = user_dict.get('uri', None)

        return User(spotify_id,
                    href=href,
                    uri=uri,
                    display_name=display_name)

    def parse_playlist(self, playlist_dict) -> SpotifyPlaylist:

        collaborative = playlist_dict.get('collaborative', None)

        ext_spotify = None
        if playlist_dict.get('external_urls', None):
            if playlist_dict['external_urls'].get('spotify', None):
                ext_spotify = playlist_dict['external_urls']['spotify']

        href = playlist_dict.get('href', None)
        description = playlist_dict.get('description', None)

        name = playlist_dict.get('name', None)

        if playlist_dict.get('owner', None):
            owner = self.parse_user(playlist_dict.get('owner'))
        else:
            owner = None

        public = playlist_dict.get('public', None)
        uri = playlist_dict.get('uri', None)

        return SpotifyPlaylist(uri=uri,
                               name=name,
                               owner=owner,
                               description=description,
                               href=href,
                               collaborative=collaborative,
                               public=public,
                               ext_spotify=ext_spotify)

    @staticmethod
    def parse_context(context_dict) -> Context:
        return Context(object_type=context_dict['type'],
                       href=context_dict['href'],
                       external_spot=context_dict['external_urls']['spotify'],
                       uri=context_dict['uri'])

    def parse_currently_playing(self, play_dict) -> CurrentlyPlaying:
        return CurrentlyPlaying(
            context=self.parse_context(play_dict['context']) if play_dict['context'] is not None else None,
            timestamp=datetime.datetime.fromtimestamp(play_dict['timestamp'] / 1000),
            progress_ms=play_dict['progress_ms'],
            is_playing=play_dict['is_playing'],
            track=self.parse_track(play_dict['item']),
            device=self.parse_device(play_dict['device']),
            shuffle=play_dict['shuffle_state'],
            repeat=play_dict['repeat_state'],
            currently_playing_type=play_dict['currently_playing_type'])

    @staticmethod
    def parse_device(device_dict) -> Device:
        return Device(device_id=device_dict['id'],
                      is_active=device_dict['is_active'],
                      is_private_session=device_dict['is_private_session'],
                      is_restricted=device_dict['is_restricted'],
                      name=device_dict['name'],
                      object_type=Device.DeviceType[device_dict['type'].upper()],
                      volume=device_dict['volume_percent'])

    @staticmethod
    def parse_audio_features(feature_dict) -> AudioFeatures:
        return AudioFeatures(acousticness=feature_dict['acousticness'],
                             analysis_url=feature_dict['analysis_url'],
                             danceability=feature_dict['danceability'],
                             duration_ms=feature_dict['duration_ms'],
                             energy=feature_dict['energy'],
                             uri=Uri(feature_dict['uri']),
                             instrumentalness=feature_dict['instrumentalness'],
                             key=feature_dict['key'],
                             liveness=feature_dict['liveness'],
                             loudness=feature_dict['loudness'],
                             mode=feature_dict['mode'],
                             speechiness=feature_dict['speechiness'],
                             tempo=feature_dict['tempo'],
                             time_signature=feature_dict['time_signature'],
                             track_href=feature_dict['track_href'],
                             valence=feature_dict['valence'])

    @staticmethod
    def chunk(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


class PageCollection:
    def __init__(self,
                 net: Network,
                 url: str = None,
                 page_limit: int = 50,
                 total_limit: int = None,
                 name: str = None,
                 page: dict = None):
        self.net = net
        self.url = url
        self.pages = []
        self.name = name
        self.page_limit = page_limit
        self.total_limit = total_limit

        if page:
            self.add_page(page)

    def __len__(self):
        length = 0
        for page in self.pages:
            length += len(page.items)
        return length

    @property
    def total(self):
        if len(self.pages) > 0:
            return self.pages[0].total
        return 0

    @property
    def items(self):
        items = []
        for page in self.pages:
            items += page.items
        return items[:self.total_limit]

    def continue_iteration(self):
        if self.total_limit:
            if len(self) < self.total_limit:
                if len(self.pages) > 0:
                    if self.pages[-1].next_link:
                        self.iterate(self.pages[-1].next_link)
                else:
                    raise IndexError('no pages')
        else:
            if len(self.pages) > 0:
                if self.pages[-1].next_link:
                    self.iterate(self.pages[-1].next_link)
            else:
                raise IndexError('no pages')

    def iterate(self, url=None):
        logger.debug(f'iterating {self.name}, {len(self.pages)}/{self.page_limit}')

        params = {'limit': self.page_limit}
        if url:
            resp = self.net.get_request(method=self.name, whole_url=url, params=params)
        else:
            if self.url:
                resp = self.net.get_request(method=self.name, url=self.url, params=params)
            else:
                raise ValueError('no url to query')

        if resp:
            page = self.add_page(resp)
            if page.next_link:
                if self.total_limit:
                    if len(self) < self.total_limit:
                        self.iterate(page.next_link)
                else:
                    self.iterate(page.next_link)
        else:
            logger.error('no response')

    def add_page(self, page_dict):
        page = self.parse_page(page_dict)
        self.pages.append(page)
        return page

    @staticmethod
    def parse_page(page_dict):
        return Page(
            href=page_dict['href'],
            items=page_dict['items'],
            response_limit=page_dict['limit'],
            next_link=page_dict['next'],
            offset=page_dict.get('offset', None),
            previous=page_dict.get('previous', None),
            total=page_dict.get('total', None))


class Page:
    def __init__(self,
                 href: str,
                 items: List,
                 response_limit: int,
                 next_link: str,
                 previous: str,
                 total: int,
                 offset: int = None):
        self.href = href
        self.items = items
        self.response_limit = response_limit
        self.next_link = next_link
        self.offset = offset
        self.previous = previous
        self.total = total
