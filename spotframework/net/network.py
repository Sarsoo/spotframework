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
from spotframework.model.track import Track, SpotifyTrack, PlaylistTrack, PlayedTrack, LibraryTrack
from spotframework.model.album import LibraryAlbum, SpotifyAlbum
from spotframework.model.service import CurrentlyPlaying, Device, Context
from spotframework.model.uri import Uri
from requests.models import Response

limit = 50

logger = logging.getLogger(__name__)


class Network:

    def __init__(self, user: NetworkUser):
        self.user = user

    def make_get_request(self, method, url=None, params=None, headers=None, whole_url=None) -> Optional[dict]:

        if headers is None:
            headers = dict()

        headers['Authorization'] = 'Bearer ' + self.user.accesstoken

        if whole_url:
            req = requests.get(whole_url, params=params, headers=headers)
        else:
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
                    return self.make_get_request(method, url, params, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self.make_get_request(method, url, params, headers)

            else:
                error_text = req.json()['error']['message']
                logger.error(f'{method} get {req.status_code} {error_text}')

        return None

    def make_post_request(self, method, url, params=None, json=None, headers=None) -> Optional[Response]:

        if headers is None:
            headers = dict()

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
                    return self.make_post_request(method, url, params, json, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self.make_post_request(method, url, params, json, headers)

            else:
                error_text = str(req.text)
                logger.error(f'{method} post {req.status_code} {error_text}')

        return None

    def make_put_request(self, method, url, params=None, json=None, headers=None) -> Optional[Response]:

        if headers is None:
            headers = dict()

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
                    return self.make_put_request(method, url, params, json, headers)
                else:
                    logger.error(f'{method} rate limit reached: cannot find Retry-After header')

            elif req.status_code == 401:
                logger.warning(f'{method} access token expired, refreshing')
                self.user.refresh_token()
                return self.make_put_request(method, url, params, json, headers)

            else:
                error_text = str(req.text)
                logger.error(f'{method} put {req.status_code} {error_text}')

        return None

    def get_playlist(self, uri: Uri) -> Optional[SpotifyPlaylist]:

        logger.info(f"{uri}")

        tracks = self.get_playlist_tracks(uri)

        if tracks is not None:

            playlist = SpotifyPlaylist(uri)
            playlist.tracks += tracks

            return playlist
        else:
            logger.error(f"{uri} - no tracks returned")
            return None

    def create_playlist(self,
                        username: str,
                        name: str = 'New Playlist',
                        public: bool = True,
                        collaborative: bool = False,
                        description: bool = None) -> Optional[SpotifyPlaylist]:

        json = {"name": name, "public": public, "collaborative": collaborative}

        if description:
            json['description'] = description

        req = self.make_post_request('createPlaylist', f'users/{username}/playlists', json=json)

        if 200 <= req.status_code < 300:
            return self.parse_playlist(req.json())
        else:
            logger.error('error creating playlist')
            return None

    def get_playlists(self, response_limit: int = None) -> Optional[List[SpotifyPlaylist]]:

        logger.info(f"loading")

        pager = PageCollection(net=self, url='me/playlists', name='getPlaylists')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_playlist(i) for i in pager.items]

        return return_items

    def get_library_albums(self, response_limit: int = None) -> Optional[List[LibraryAlbum]]:

        logger.info(f"loading")

        pager = PageCollection(net=self, url='me/albums', name='getLibraryAlbums')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_album(i) for i in pager.items]

        return return_items

    def get_library_tracks(self, response_limit: int = None) -> Optional[List[LibraryAlbum]]:

        logger.info(f"loading")

        pager = PageCollection(net=self, url='me/tracks', name='getLibraryTracks')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_track(i) for i in pager.items]

        return return_items

    def get_user_playlists(self) -> Optional[List[SpotifyPlaylist]]:

        logger.info('retrieved')

        playlists = self.get_playlists()

        if playlists:
            return list(filter(lambda x: x.owner.username == self.user.username, playlists))
        else:
            logger.error('no playlists returned to filter')
            return None

    def get_playlist_tracks(self, uri: Uri, response_limit: int = None) -> List[PlaylistTrack]:

        logger.info(f"loading")

        pager = PageCollection(net=self, url=f'playlists/{uri.object_id}/tracks', name='getPlaylistTracks')
        if response_limit:
            pager.total_limit = response_limit
        pager.iterate()

        return_items = [self.parse_track(i) for i in pager.items]

        return return_items

    def get_available_devices(self) -> Optional[List[Device]]:

        logger.info("retrieving")

        resp = self.make_get_request('getAvailableDevices', 'me/player/devices')
        if resp:
            return [self.parse_device(i) for i in resp['devices']]
        else:
            logger.error('no devices returned')
            return None

    def get_recently_played_tracks(self,
                                   response_limit: int = None,
                                   after: datetime.datetime = None,
                                   before: datetime.datetime = None) -> Optional[List[PlayedTrack]]:
        logger.info("retrieving")

        params = dict()
        if after and before:
            raise ValueError('cant have before and after')
        if after:
            params['after'] = int(after.timestamp() * 1000)
        if before:
            params['before'] = int(before.timestamp() * 1000)

        resp = self.make_get_request('getRecentlyPlayedTracks', 'me/player/recently-played', params=params)

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
            return None

    def get_player(self) -> Optional[CurrentlyPlaying]:

        logger.info("retrieved")

        resp = self.make_get_request('getPlayer', 'me/player')
        if resp:
            return self.parse_currently_playing(resp)
        else:
            logger.info('no player returned')
            return None

    def get_device_id(self, devicename: str) -> Optional[str]:

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

    def change_playback_device(self, device_id: str):

        logger.info(device_id)

        json = {
            'device_ids': [device_id],
            'play': True
        }

        resp = self.make_put_request('changePlaybackDevice', 'me/player', json=json)
        if resp:
            return True
        else:
            return None

    def play(self, uri: Uri = None, uris: List[Uri] = None, deviceid: str = None) -> Optional[Response]:

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

        req = self.make_put_request('play', 'me/player/play', params=params, json=payload)
        if req:
            return req
        else:
            logger.error('error playing')

    def pause(self, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.make_put_request('pause', 'me/player/pause', params=params)
        if req:
            return req
        else:
            logger.error('error pausing')

    def next(self, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.make_post_request('next', 'me/player/next', params=params)
        if req:
            return req
        else:
            logger.error('error skipping')

    def previous(self, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{deviceid if deviceid is not None else ''}")

        if deviceid is not None:
            params = {'device_id': deviceid}
        else:
            params = None

        req = self.make_post_request('previous', 'me/player/previous', params=params)
        if req:
            return req
        else:
            logger.error('error reversing')

    def set_shuffle(self, state: bool, deviceid: str = None) -> Optional[Response]:

        logger.info(f"{state}{' ' + deviceid if deviceid is not None else ''}")

        params = {'state': str(state).lower()}

        if deviceid is not None:
            params['device_id'] = deviceid

        req = self.make_put_request('setShuffle', 'me/player/shuffle', params=params)
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

            req = self.make_put_request('setVolume', 'me/player/volume', params=params)
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

        req = self.make_put_request('replacePlaylistTracks', f'playlists/{uri.object_id}/tracks',
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
            req = self.make_put_request('changePlaylistDetails', f'playlists/{uri.object_id}',
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

        req = self.make_post_request('addPlaylistTracks', f'playlists/{uri.object_id}/tracks',
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
            resp = self.make_get_request('getRecommendations', 'recommendations', params=params)
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

        if playlist.uri:
            if playlist.tracks == -1:
                self.replace_playlist_tracks(playlist.uri, [])
            elif playlist.tracks:
                if append_tracks:
                    self.add_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks if
                                                            isinstance(i, SpotifyTrack)])
                else:
                    self.replace_playlist_tracks(playlist.uri, [i.uri for i in playlist.tracks if
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

        resp = self.make_put_request('reorderPlaylistTracks', f'playlists/{uri.object_id}/tracks', json=json)

        if resp:
            return resp
        else:
            logger.error('error reordering playlist')

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

                                href=href,
                                uri=uri,

                                genres=genres,
                                tracks=tracks,

                                release_date=release_date,
                                release_date_precision=release_date_precision,

                                label=label,
                                popularity=popularity)

    def parse_track(self, track_dict) -> Union[Track, SpotifyTrack, PlaylistTrack, PlayedTrack]:

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
        if len(self) < self.total_limit:
            if len(self.pages) > 0:
                if self.pages[-1].next_link:
                    self.iterate(self.pages[-1].next_link)
            else:
                raise IndexError('no pages')

    def iterate(self, url=None):
        logger.debug(f'iterating {self.name}')

        params = {'limit': self.page_limit}
        if url:
            resp = self.net.make_get_request(method=self.name, whole_url=url, params=params)
        else:
            if self.url:
                resp = self.net.make_get_request(method=self.name, url=self.url, params=params)
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
