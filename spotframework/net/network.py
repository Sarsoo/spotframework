import requests
import random
import logging
import time
from dataclasses import dataclass
from typing import List, Optional, Union
import datetime

from spotframework.model.artist import ArtistFull
from spotframework.model.user import PublicUser
from . import const
from spotframework.net.user import NetworkUser
from spotframework.model.playlist import SimplifiedPlaylist, FullPlaylist
from spotframework.model.track import SimplifiedTrack, TrackFull, PlaylistTrack, PlayedTrack, LibraryTrack, \
    AudioFeatures, Device, CurrentlyPlaying, Recommendations
from spotframework.model.album import AlbumFull, LibraryAlbum, SimplifiedAlbum
from spotframework.model.uri import Uri
from requests.models import Response

limit = 50

logger = logging.getLogger(__name__)


@dataclass
class SearchResponse:
    tracks: List[TrackFull]
    albums: List[SimplifiedAlbum]
    artists: List[ArtistFull]
    playlists: List[SimplifiedPlaylist]

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
                self.user.refresh_access_token()
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
                self.user.refresh_access_token()
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
                self.user.refresh_access_token()
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
                     tracks: bool = True) -> Optional[FullPlaylist]:
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
            playlist = FullPlaylist(**resp)

            if resp.get('tracks'):
                if 'next' in resp['tracks']:
                    logger.debug(f'paging tracks for {uri}')

                    track_pager = PageCollection(net=self, page=resp['tracks'])
                    track_pager.continue_iteration()

                    playlist.tracks = [PlaylistTrack(**i) for i in track_pager.items]
                else:
                    logger.debug(f'parsing {len(resp.get("tracks"))} tracks for {uri}')
                    playlist.tracks = [PlaylistTrack(**i) for i in resp.get('tracks', [])]

            return playlist
        else:
            logger.error('no playlist returned')
            return None

    def create_playlist(self,
                        username: str,
                        name: str = 'New Playlist',
                        public: bool = True,
                        collaborative: bool = False,
                        description: bool = None) -> Optional[FullPlaylist]:
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
            return FullPlaylist(**req.json())
        else:
            logger.error('error creating playlist')
            return None

    def get_playlists(self, response_limit: int = None) -> Optional[List[FullPlaylist]]:
        """get current users playlists

        :param response_limit: max playlists to return
        :return: List of user created and followed playlists if available
        """

        logger.info(f"paging playlists")

        pager = PageCollection(net=self, url='me/playlists', name='getPlaylists')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [SimplifiedPlaylist(**i) for i in pager.items]

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

        return_items = [LibraryAlbum(**i) for i in pager.items]

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

        return_items = [LibraryTrack(**i) for i in pager.items]

        if len(return_items) == 0:
            logger.error('no tracks returned')

        return return_items

    def get_user_playlists(self) -> Optional[List[FullPlaylist]]:
        """retrieve user owned playlists

        :return: List of user owned playlists if available
        """

        logger.info('pulling all playlists')

        playlists = self.get_playlists()

        if self.user.user.id is None:
            logger.debug('no user info, refreshing for filter')
            self.user.refresh_info()

        if playlists is not None:
            return list(filter(lambda x: x.owner.id == self.user.user.id, playlists))
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

        return_items = [PlaylistTrack(**i) for i in pager.items]

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
            return [Device(**i) for i in resp['devices']]
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

            return [PlayedTrack(**i) for i in pager.items]
        else:
            logger.error('no tracks returned')

    def get_player(self) -> Optional[CurrentlyPlaying]:
        """get currently playing snapshot (player)"""

        logger.info("polling player")

        resp = self.get_request('getPlayer', 'me/player')
        if resp:
            return CurrentlyPlaying(**resp)
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
                return device.id
            else:
                logger.error(f'{device_name} not found')
        else:
            logger.error('no devices returned')

    def get_current_user(self) -> Optional[PublicUser]:
        logger.info(f"getting current user")

        resp = self.get_request('getCurrentUser', 'me')
        if resp:
            return PublicUser(**resp)
        else:
            logger.info('no user returned')

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
                            tracks: List[str] = None,
                            artists: List[str] = None,
                            response_limit=10) -> Optional[Recommendations]:

        logger.info(f'getting {response_limit} recommendations, '
                    f'tracks: {len(tracks) if tracks is not None else 0}, '
                    f'artists: {len(artists) if artists is not None else 0}')

        params = {'limit': response_limit}

        if tracks:
            random.shuffle(tracks)
            params['seed_tracks'] = tracks[:5]
        if artists:
            random.shuffle(artists)
            params['seed_artists'] = artists[:5]

        if len(params) == 1:
            logger.warning('update dictionairy length 0')
            return None
        else:
            resp = self.get_request('getRecommendations', 'recommendations', params=params)
            if resp:
                return Recommendations(**resp)
            else:
                logger.error('error getting recommendations')
                return None

    def write_playlist_object(self,
                              playlist: FullPlaylist,
                              append_tracks: bool = False):
        logger.info(f'writing {playlist.name}, append tracks: {append_tracks}')

        if playlist.uri:
            if playlist.tracks == -1:
                logger.debug(f'wiping {playlist.name} tracks')
                self.replace_playlist_tracks(uri=playlist.uri, uris=[])
            elif playlist.tracks:
                if append_tracks:
                    self.add_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks if
                                                            isinstance(i, SimplifiedTrack)])
                else:
                    self.replace_playlist_tracks(uri=playlist.uri, uris=[i.uri for i in playlist.tracks if
                                                                         isinstance(i, SimplifiedTrack)])

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

    def get_track_audio_features(self, uris: List[Uri]) -> Optional[List[AudioFeatures]]:
        logger.info(f'getting {len(uris)} features')

        audio_features = []
        chunked_uris = list(self.chunk(uris, 100))
        for chunk in chunked_uris:
            resp = self.get_request('getAudioFeatures',
                                    url='audio-features',
                                    params={'ids': ','.join(i.object_id for i in chunk)})

            if resp:
                if resp.get('audio_features', None):
                    return [AudioFeatures(**i) for i in resp['audio_features']]
                else:
                    logger.error('no audio features included')
            else:
                logger.error('no response')

        if len(audio_features) == len(uris):
            return audio_features
        else:
            logger.error('mismatched length of input and response')

    def populate_track_audio_features(self, tracks=Union[TrackFull, List[TrackFull]]):
        logger.info(f'populating {len(tracks)} features')

        if isinstance(tracks, TrackFull):
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
            if all(isinstance(i, TrackFull) for i in tracks):
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
                   uri_strings: List[str] = None) -> List[TrackFull]:

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
                tracks += [TrackFull(**i) for i in resp.get('tracks', [])]

        return tracks

    def get_track(self, uri: Uri = None, uri_string: str = None) -> Optional[TrackFull]:

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        track = self.get_tracks([uri])
        if len(track) == 1:
            return track[0]
        else:
            return None

    def get_albums(self, uris: List[Uri] = None, uri_strings: List[str] = None) -> List[AlbumFull]:

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
                albums += [AlbumFull(**i) for i in resp.get('albums', [])]

        return albums

    def get_album(self, uri: Uri = None, uri_string: str = None) -> Optional[AlbumFull]:

        if uri is None and uri_string is None:
            raise NameError('no uri provided')

        if uri_string is not None:
            uri = Uri(uri_string)

        album = self.get_albums([uri])
        if len(album) == 1:
            return album[0]
        else:
            return None

    def get_artists(self, uris: List[Uri] = None, uri_strings: List[str] = None) -> List[ArtistFull]:

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
                artists += [ArtistFull(**i) for i in resp.get('artists', [])]

        return artists

    def get_artist(self, uri: Uri = None, uri_string: str = None) -> Optional[ArtistFull]:

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

        albums = [SimplifiedAlbum(**i) for i in resp.get('albums', {}).get('items', [])]
        artists = [ArtistFull(**i) for i in resp.get('artists', {}).get('items', [])]
        tracks = [TrackFull(**i) for i in resp.get('tracks', {}).get('items', [])]
        playlists = [SimplifiedPlaylist(**i) for i in resp.get('playlists', {}).get('items', [])]

        return SearchResponse(tracks=tracks, albums=albums, artists=artists, playlists=playlists)

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
