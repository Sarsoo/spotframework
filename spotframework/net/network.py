import requests
import random
import logging
import time
from base64 import b64encode
from dataclasses import dataclass
from typing import List, Optional, Union
import datetime
from json import JSONDecodeError

from spotframework.model.artist import ArtistFull
from spotframework.model.user import PublicUser
from spotframework.net.user import NetworkUser
from spotframework.model.playlist import SimplifiedPlaylist, FullPlaylist
from spotframework.model.track import SimplifiedTrack, TrackFull, PlaylistTrack, PlayedTrack, LibraryTrack, \
    AudioFeatures, Device, CurrentlyPlaying, Recommendations
from spotframework.model.album import AlbumFull, LibraryAlbum, SimplifiedAlbum
from spotframework.model.uri import Uri

limit = 50

logger = logging.getLogger(__name__)


@dataclass
class SpotifyNetworkException(Exception):
    http_code: int
    message: str = None

    def __str__(self):
        return "Spotify Network Exception: (%s) %s" % (self.http_code, self.message)


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

    api_root = 'https://api.spotify.com/v1/'

    def __init__(self, user: NetworkUser):
        """Create network using NetworkUser containing credentials

        :param user: target spotify user
        """
        self.user = user
        self.refresh_counter = 0
        self.rsession = requests.Session()

    def net_call(self,
                 method: str,
                 url_path: str = None,
                 whole_url: str = None,
                 params: dict = None,
                 data: dict = None,
                 json: dict = None,
                 headers: dict = None,
                 auth: bool = True,
                 **kwargs) -> Optional[dict]:

        method = method.strip().upper()

        if not url_path and not whole_url:
            raise KeyError("No URL provided for request")

        if whole_url:
            url = whole_url
        else:
            url = Network.api_root + url_path

        if not headers:
            headers = dict()

        if auth:
            headers['Authorization'] = 'Bearer ' + self.user.access_token

        if kwargs:
            if method in ['GET', 'DELETE']:
                if not params:
                    params = dict()
                params.update({i: j for i, j in kwargs.items() if j is not None})
            elif method in ['POST', 'PUT']:
                if not json:
                    json = dict()
                json.update({i: j for i, j in kwargs.items() if j is not None})

        response = self.rsession.request(method=method,
                                         url=url,
                                         headers=headers,
                                         params=params,
                                         json=json,
                                         data=data)

        if 200 <= response.status_code < 300:
            logger.debug(f'{method} {url_path or whole_url} {response.status_code}')

            if response.status_code == 204:
                return None

            try:
                return response.json()
            except JSONDecodeError:
                return None
        else:
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', None)

                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    if retry_after:
                        logger.warning(f'{method} {url_path or whole_url} rate limit reached: '
                                       f'retrying in {retry_after} seconds')
                        time.sleep(int(retry_after) + 1)
                        return self.net_call(method=method,
                                             url_path=url_path,
                                             whole_url=whole_url,
                                             params=params,
                                             data=data,
                                             json=json,
                                             headers=headers)
                    else:
                        logger.error(f'{method} {url_path or whole_url} rate limit reached: '
                                     f'cannot find Retry-After header')
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} {url_path or whole_url} refresh token limit (5) reached')

            elif response.status_code == 401:
                logger.warning(f'{method} {url_path or whole_url} access token expired, refreshing')
                self.refresh_access_token()
                if self.refresh_counter < 5:
                    self.refresh_counter += 1
                    return self.net_call(method=method,
                                         url_path=url_path,
                                         whole_url=whole_url,
                                         params=params,
                                         data=data,
                                         json=json,
                                         headers=headers)
                else:
                    self.refresh_counter = 0
                    logger.critical(f'{method} {url_path or whole_url} refresh token limit (5) reached')

            try:
                error_json = response.json()["error"]
                logger.error(f'{method} {response.status_code} {error_json["message"]}')
                raise SpotifyNetworkException(http_code=response.status_code, message=error_json["message"])
            except (KeyError, JSONDecodeError):
                logger.error(f'{method} {response.status_code} no error object found')
                raise SpotifyNetworkException(http_code=response.status_code, message=response.text)

    def get_request(self, url=None, params=None, headers=None, whole_url=None, auth=True, **kwargs) -> Optional[dict]:
        """HTTP get request for reading from service

        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param headers: additional request headers
        :param whole_url: override base api url with new hostname and url
        :param auth: direct bearer authentication header to be injected
        :return: dictionary of json response if available
        """

        return self.net_call(method='GET', url_path=url, whole_url=whole_url, params=params,
                             headers=headers, auth=auth, **kwargs)

    def post_request(self, url=None, params=None, json=None, data=None,
                     headers=None, whole_url=None, auth=True, **kwargs) -> Optional[dict]:
        """HTTP post request for reading from service

        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param json: dictionary request body for conversion to json during transmission
        :param data: dictionary request body for transmission
        :param headers: additional request headers
        :param whole_url: override base api url with new hostname and url
        :param auth: direct bearer authentication header to be injected
        :return: response object if available
        """

        return self.net_call(method='POST', url_path=url, whole_url=whole_url, params=params,
                             json=json, data=data, headers=headers, auth=auth, **kwargs)

    def put_request(self, url=None, params=None, json=None, data=None,
                    headers=None, whole_url=None, auth=True, **kwargs) -> Optional[dict]:
        """HTTP put request for reading from service

        :param url: query url string following hostname and api version
        :param params: dictionary of query parameters
        :param json: dictionary request body for conversion to json during transmission
        :param data: dictionary request body for transmission
        :param headers: additional request headers
        :param whole_url: override base api url with new hostname and url
        :param auth: direct bearer authentication header to be injected
        :return: response object if available
        """

        return self.net_call(method='PUT', url_path=url, whole_url=whole_url, params=params,
                             json=json, data=data, headers=headers, auth=auth, **kwargs)

    def refresh_access_token(self):
        logger.info(f'refreshing token')

        if self.user.refresh_token is None:
            raise NameError('no refresh token to query')

        if self.user.client_id is None:
            raise NameError('no client id')

        if self.user.client_secret is None:
            raise NameError('no client secret')

        idsecret = b64encode(bytes(self.user.client_id + ':' + self.user.client_secret, "utf-8")).decode("ascii")
        headers = {'Authorization': 'Basic %s' % idsecret}

        try:
            resp = self.post_request(headers=headers,
                                     whole_url='https://accounts.spotify.com/api/token',
                                     auth=False,
                                     data={"grant_type": "refresh_token",
                                           "refresh_token": self.user.refresh_token})

            self.user.access_token = resp['access_token']
            if resp.get('refresh_token', None):
                self.user.refresh_token = resp['refresh_token']
            self.user.token_expiry = resp['expires_in']
            self.user.last_refreshed = datetime.datetime.utcnow()
            for func in self.user.on_refresh:
                func(self.user)
        except SpotifyNetworkException as e:
            logger.error(f'error refreshing user token - {e}')

        return self

    def refresh_user_info(self):
        self.user.user = self.get_current_user()

    def get_playlist(self,
                     uri: Uri = None,
                     uri_string: str = None,
                     tracks: bool = True) -> FullPlaylist:
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

        resp = self.get_request(f'playlists/{uri.object_id}')
        playlist = FullPlaylist(**resp)

        if resp.get('tracks') and tracks:
            if 'next' in resp['tracks']:
                logger.debug(f'paging tracks for {uri}')

                track_pager = PageCollection(net=self, page=resp['tracks'])
                track_pager.continue_iteration()

                playlist.tracks = [PlaylistTrack(**i) for i in track_pager.items]
            else:
                logger.debug(f'parsing {len(resp.get("tracks"))} tracks for {uri}')
                playlist.tracks = [PlaylistTrack(**i) for i in resp.get('tracks', [])]

        return playlist

    def create_playlist(self,
                        username: str,
                        name: str = 'New Playlist',
                        public: bool = True,
                        collaborative: bool = False,
                        description: str = None) -> FullPlaylist:
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

        if collaborative and public:
            public = False
            logger.warning(f'public collaborative playlist requested, defaulting to private {username} / {name}')

        req = self.post_request(f'users/{username}/playlists',
                                name=name,
                                public=public,
                                collaborative=collaborative,
                                description=description)
        return FullPlaylist(**req)

    def get_playlists(self, response_limit: int = None) -> Optional[List[SimplifiedPlaylist]]:
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

    def get_user_playlists(self) -> List[SimplifiedPlaylist]:
        """retrieve user owned playlists

        :return: List of user owned playlists if available
        """

        logger.info('pulling all playlists')

        playlists = self.get_playlists()

        if self.user.user.id is None:
            logger.debug('no user info, refreshing for filter')
            self.refresh_user_info()

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

    def get_available_devices(self) -> List[Device]:
        """get users available devices"""

        logger.info("polling available devices")

        resp = self.get_request('me/player/devices')

        if len(resp['devices']) == 0:
            logger.error('no devices returned')
        return [Device(**i) for i in resp['devices']]

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

        resp = self.get_request('me/player/recently-played', params=params)

        pager = PageCollection(self, page=resp)
        if response_limit:
            pager.total_limit = response_limit
        else:
            pager.total_limit = 20
        pager.continue_iteration()

        return [PlayedTrack(**i) for i in pager.items]

    def get_player(self) -> CurrentlyPlaying:
        """get currently playing snapshot (player)"""

        logger.info("polling player")

        resp = self.get_request('me/player')
        return CurrentlyPlaying(**resp)

    def get_device_id(self, device_name: str) -> Optional[str]:
        """return device id of device as searched for by name

        :param device_name: target device name
        :return: device ID
        """

        logger.info(f"querying {device_name}")

        devices = self.get_available_devices()
        device = next((i for i in devices if i.name == device_name), None)
        if device:
            return device.id
        else:
            logger.error(f'{device_name} not found')

    def get_current_user(self) -> PublicUser:
        logger.info(f"getting current user")

        resp = self.get_request('me')
        return PublicUser(**resp)

    def change_playback_device(self, device_id: str):
        """migrate playback to different device"""
        logger.info(f'shifting playback to {device_id}')
        self.put_request('me/player', device_ids=[device_id], play=True)

    def play(self,
             uri: Uri = None,
             uri_string: str = None,
             uris: List[Uri] = None,
             uri_strings: List[str] = None,
             deviceid: str = None):
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

        self.put_request('me/player/play', params=params, json=payload)

    def pause(self, deviceid: str = None):
        """pause playback"""

        logger.info(f"{deviceid or ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        self.put_request('me/player/pause', params=params)

    def next(self, deviceid: str = None):
        """skip track playback"""

        logger.info(f"{deviceid or ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        self.post_request('me/player/next', params=params)

    def previous(self, deviceid: str = None):
        """skip playback backwards"""

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        self.post_request('me/player/previous', params=params)

    def set_shuffle(self, state: bool, deviceid: str = None):

        logger.info(f"{state}{' ' + deviceid if deviceid is not None else ''}")

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        return self.put_request('me/player/shuffle', params=params)

    def set_volume(self, volume: int, deviceid: str = None):

        logger.info(f"{volume}{' ' + deviceid if deviceid is not None else ''}")

        if 0 <= int(volume) <= 100:

            params = {'volume_percent': volume}
            if deviceid is not None:
                params['device_id'] = deviceid

            self.put_request('me/player/volume', params=params)

        else:
            logger.error(f"{volume} not accepted value")

    def replace_playlist_tracks(self,
                                uri: Uri = None,
                                uri_string: str = None,
                                uris: List[Uri] = None,
                                uri_strings: List[str] = None) -> Optional[List[str]]:

        if uri_string is not None:
            uri = Uri(uri_string)

        if uri_strings is not None:
            uris = [Uri(i) for i in uri_strings]

        logger.info(f"replacing {uri} with {'0' if uris is None else len(uris)} tracks")

        self.put_request(f'playlists/{uri.object_id}/tracks', uris=[str(i) for i in uris[:100]])

        if len(uris) > 100:
            return self.add_playlist_tracks(uri, uris[100:])

    def change_playlist_details(self,
                                uri: Uri,
                                name: str = None,
                                public: bool = None,
                                collaborative: bool = None,
                                description: str = None):

        logger.info(f"updating {uri}, name: {name}, public: {public}, collab: {collaborative}, "
                    f"description: {(description[:30] + '...' if len(description) > 33 else description) if description is not None else None}")

        if all(v is None for v in [name, public, collaborative, description]):
            logger.warning('update dictionairy length 0')
        else:
            self.put_request(f'playlists/{uri.object_id}',
                             name=name,
                             public=public,
                             collaborative=collaborative,
                             description=description)

    def add_playlist_tracks(self, uri: Uri, uris: List[Uri]) -> List[str]:

        logger.info(f"adding {len(uris)} tracks to {uri}")

        snapshot_ids = [
            self.post_request(f'playlists/{uri.object_id}/tracks',
                              uris=[str(i) for i in uris[:100]])["snapshot_id"]
        ]

        if len(uris) > 100:
            snapshot_ids += self.add_playlist_tracks(uri, uris[100:])

        return snapshot_ids

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
        else:
            return Recommendations(**self.get_request('recommendations', params=params))

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
                                insert_before: int) -> dict:

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

        return self.put_request(f'playlists/{uri.object_id}/tracks',
                                range_start=range_start,
                                range_length=range_length,
                                insert_before=insert_before)

    def get_track_audio_features(self, uris: List[Uri]) -> Optional[List[AudioFeatures]]:
        logger.info(f'getting {len(uris)} features')

        audio_features = []
        chunked_uris = list(self.chunk(uris, 100))
        for chunk in chunked_uris:
            resp = self.get_request(url='audio-features', ids=','.join(i.object_id for i in chunk))

            if resp.get('audio_features', None):
                return [AudioFeatures(**i) for i in resp['audio_features']]
            else:
                logger.error('no audio features included')

        if len(audio_features) == len(uris):
            return audio_features
        else:
            logger.error('mismatched length of input and response')

    def populate_track_audio_features(self, tracks=Union[SimplifiedTrack, List[SimplifiedTrack]]):
        logger.info(f'populating {len(tracks)} features')

        if isinstance(tracks, SimplifiedTrack):
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
            if all(isinstance(i, SimplifiedTrack) for i in tracks):
                audio_features = self.get_track_audio_features([i.uri for i in tracks])

                if audio_features:
                    if len(audio_features) != len(tracks):
                        logger.error(f'{len(audio_features)} features returned for {len(tracks)} tracks')

                    for track, audio_feature in zip(tracks, audio_features):
                        track.audio_features = audio_feature

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
            resp = self.get_request(url='tracks', ids=','.join([i.object_id for i in chunk]))
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
            resp = self.get_request(url='albums', ids=','.join([i.object_id for i in chunk]))
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
            resp = self.get_request(url='artists', ids=','.join([i.object_id for i in chunk]))
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

        logger.info(f'querying track: {track}, album: {album}, artist: {artist}')

        resp = self.get_request(url='search',
                                q=' '.join(queries),
                                type=','.join([i.name for i in query_types]),
                                limit=response_limit)

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
            if len(self) >= self.total_limit:
                return

        if len(self.pages) > 0:
            if self.pages[-1].next:
                self.iterate(self.pages[-1].next)
        else:
            raise IndexError('no pages')

    def iterate(self, url=None):
        logger.debug(f'iterating {self.name}, {len(self.pages)}/{self.page_limit}')

        params = {'limit': self.page_limit}
        if url:
            resp = self.net.get_request(whole_url=url, params=params)
        else:
            if self.url:
                resp = self.net.get_request(url=self.url, params=params)
            else:
                raise ValueError('no url to query')

        page = self.add_page(resp)
        if page.next:
            if self.total_limit:
                if len(self) < self.total_limit:
                    self.iterate(page.next)
            else:
                self.iterate(page.next)

    def add_page(self, page_dict):
        page = Page(**page_dict)
        self.pages.append(page)
        return page


@dataclass
class Page:
    href: str
    items: List
    limit: int
    next: str
    previous: str
    total: int
    offset: int = None
