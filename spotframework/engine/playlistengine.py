import logging
import copy
from abc import ABC, abstractmethod

import spotframework.util.monthstrings as monthstrings
from spotframework.engine.processor.added import AddedSince

from typing import List, Optional
from spotframework.model.track import SpotifyTrack
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.model.uri import Uri
from spotframework.net.network import Network
from spotframework.engine.processor.abstract import AbstractProcessor
from datetime import datetime
from requests.models import Response

logger = logging.getLogger(__name__)


class SourceParameter:
    def __init__(self,
                 source_type,
                 processors: List[AbstractProcessor] = None):
        self.processors = processors if processors is not None else []
        self.source_type = source_type


class PlaylistEngine:

    def __init__(self, net: Network):
        self.sources = []
        self.net = net

    def init_default_sources(self):
        self.sources = [PlaylistSource(self.net), RecommendationSource(self.net)]

    def check_for_source(self, class_type) -> bool:
        source = next((i for i in self.sources if isinstance(i, class_type)), None)

        if source:
            return True
        else:
            return False

    def get_source(self, class_type):
        return next((i for i in self.sources if isinstance(i, class_type)), None)

    def make_playlist(self,
                      params: List[SourceParameter],
                      processors: List[AbstractProcessor] = None) -> List[SpotifyTrack]:

        tracks = []

        for param in params:
            source = next((i for i in self.sources if isinstance(i, param.source_type)), None)
            if source:
                if source.loaded is False:
                    source.load()

                if isinstance(source, RecommendationSource) and isinstance(param, RecommendationSource.Params):
                    tracks += source.process(params=param, uris=[i.uri for i in tracks])
                else:
                    tracks += source.process(params=param)
            else:
                new_source = param.source_type(net=self.net)
                new_source.load()
                self.sources.append(new_source)

                if isinstance(new_source, RecommendationSource) and isinstance(param, RecommendationSource.Params):
                    tracks += new_source.process(params=param, uris=[i.uri for i in tracks])
                else:
                    tracks += new_source.process(params=param)

                logger.info(f'adding {str(param.source_type)} source')

        if processors:
            for processor in processors:
                tracks = processor.process(tracks)

        return tracks

    def get_recent_playlist(self,
                            params: List[SourceParameter],
                            boundary_date: datetime,
                            processors: List[AbstractProcessor] = None,
                            add_this_month: bool = False,
                            add_last_month: bool = False) -> List[SpotifyTrack]:
        if processors is None:
            processors = []

        this_month = monthstrings.get_this_month()
        last_month = monthstrings.get_last_month()

        month_playlists = []

        if add_this_month:
            month_playlists.append(this_month)

        if add_last_month:
            month_playlists.append(last_month)

        if PlaylistSource in [i.source_type for i in params]:

            param = next((i for i in params if i.source_type == PlaylistSource), None)
            param.names += month_playlists

        return self.make_playlist(params=params, processors=processors + [AddedSince(boundary_date)])

    def reorder_playlist_by_added_date(self,
                                       name: str = None,
                                       uri: Uri = None,
                                       reverse: bool = False):
        if name is None and uri is None:
            logger.error('no playlist name or id provided')
            raise ValueError('no playlist name or id provided')

        playlist_source = self.get_source(PlaylistSource)

        if playlist_source:
            if playlist_source.loaded is False:
                playlist_source.load()
        else:
            playlist_source = PlaylistSource(self.net)
            playlist_source.load()
            self.sources.append(playlist_source)

        if name:
            playlist = next((i for i in playlist_source.playlists if i.name == name), None)
        else:

            if uri.object_type is not Uri.ObjectType.playlist:
                raise TypeError('uri not a playlist')

            playlist = next((i for i in playlist_source.playlists if i.uri == uri), None)

        if playlist is None:
            logger.error('playlist not found')
            return None

        if playlist.has_tracks() is False:
            playlist_source.get_playlist_tracks(playlist)

        tracks_to_sort = list(playlist.tracks)
        for i in range(len(playlist)):
            counter_track = tracks_to_sort[0]
            for track in tracks_to_sort:
                if reverse is False:
                    if counter_track.added_at > track.added_at:
                        counter_track = track
                else:
                    if counter_track.added_at < track.added_at:
                        counter_track = track

            if counter_track != tracks_to_sort[0]:
                self.net.reorder_playlist_tracks(playlist.uri,
                                                 i + tracks_to_sort.index(counter_track),
                                                 1, i)
            tracks_to_sort.remove(counter_track)

    def execute_playlist(self,
                         tracks: List[SpotifyTrack],
                         uri: Uri) -> Optional[Response]:

        resp = self.net.replace_playlist_tracks(uri=uri, uris=[i.uri for i in tracks])
        if resp:
            return resp
        else:
            logger.error('error executing')
            return None

    def change_description(self,
                           playlistparts: List[str],
                           uri: Uri,
                           overwrite: bool = None,
                           suffix: str = None) -> Optional[Response]:

        if overwrite:
            string = overwrite
        else:
            string = ' / '.join(playlistparts)

        if suffix:
            string += f' - {str(suffix)}'

        resp = self.net.change_playlist_details(uri, description=string)
        if resp:
            return resp
        else:
            logger.error('error changing description')


class TrackSource(ABC):

    def __init__(self, net: Network):
        self.net = net
        self.loaded = False

    @abstractmethod
    def load(self) -> None:
        self.loaded = True

    @abstractmethod
    def process(self, params: SourceParameter) -> List[SpotifyTrack]:
        pass


class PlaylistSource(TrackSource):

    class Params(SourceParameter):
        def __init__(self,
                     names: List[str] = None,
                     uris: List[Uri] = None,
                     processors: List[AbstractProcessor] = None):
            self.names = names if names is not None else []
            self.uris = uris if uris is not None else []
            super().__init__(processors=processors, source_type=PlaylistSource)

    def __init__(self,
                 net: Network):
        self.playlists = []
        super().__init__(net)

    def append_user_playlists(self) -> None:
        logger.info('appending user playlists')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists += playlists
        else:
            logger.error('error getting playlists')

    def get_playlist_tracks(self,
                            playlist: SpotifyPlaylist) -> None:
        logger.info(f"pulling tracks for {playlist.name}")

        tracks = self.net.get_playlist_tracks(playlist.uri)
        if tracks and len(tracks) > 0:
            playlist.tracks = tracks
        else:
            logger.error('error getting tracks')

    def load(self) -> None:
        logger.info('loading user playlists')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists = playlists
        else:
            logger.error('error getting playlists')

        super().load()

    def process(self, params: Params) -> List[SpotifyTrack]:

        playlists = []

        for name in params.names:
            playlist = next((i for i in self.playlists if i.name == name), None)
            if playlist is not None:
                playlists.append(playlist)
            else:
                logger.warning(f'could not find playlist {name}')

        for uri in params.uris:
            playlist = next((i for i in self.playlists if i.uri == uri), None)
            if playlist:
                playlists.append(playlist)
            else:
                playlist = self.net.get_playlist(uri)
                if playlist:
                    playlists.append(playlist)
                    self.playlists.append(playlist)

                else:
                    logger.warning(f'could not find playlist {uri}')

        tracks = []
        for playlist in playlists:
            if playlist.has_tracks() is False:
                self.get_playlist_tracks(playlist)

            playlist_tracks = copy.deepcopy(playlist.tracks)

            for processor in [i for i in params.processors if i.has_targets()]:
                if playlist.name in [i for i in processor.playlist_names]\
                        or playlist.uri in [i for i in processor.playlist_uris]:
                    playlist_tracks = processor.process(playlist_tracks)

            tracks += [i for i in playlist_tracks if i.is_local is False]

        for processor in [i for i in params.processors if i.has_targets() is False]:
            tracks = processor.process(tracks)

        return tracks


class LibraryTrackSource(TrackSource):

    class Params(SourceParameter):
        def __init__(self, processors: List[AbstractProcessor] = None):
            super().__init__(processors=processors, source_type=LibraryTrackSource)

    def __init__(self,
                 net: Network):
        self.tracks = []
        super().__init__(net)

    def load(self) -> None:
        logger.info('loading library tracks')

        tracks = self.net.get_library_tracks()
        if tracks and len(tracks) > 0:
            self.tracks = tracks
        else:
            logger.error('error getting tracks')

        super().load()

    def process(self, params: SourceParameter) -> List[SpotifyTrack]:

        tracks = copy.deepcopy(self.tracks)

        for index, track in enumerate(tracks):
            for processor in [i for i in params.processors if i.playlist_uris]:
                if track.uri in [i for i in processor.playlist_uris]:
                    new_track = processor.process([track])

                    if new_track and len(new_track) > 0:
                        tracks[index] = new_track[0]
                    else:
                        tracks[index] = None

        tracks = [i for i in tracks if i is not None]

        for processor in [i for i in params.processors if i.has_targets() is False]:
            tracks = processor.process(tracks)

        return tracks


class RecommendationSource(TrackSource):

    class Params(SourceParameter):
        def __init__(self,
                     uris: List[Uri] = None,
                     recommendation_limit: int = None,
                     processors: List[AbstractProcessor] = None):
            self.uris = uris
            self.recommendation_limit = recommendation_limit if recommendation_limit is not None else 10
            super().__init__(processors=processors, source_type=RecommendationSource)

    def load(self):
        super().load()

    def process(self, params: Params, uris: List[Uri] = None):

        query_uris = []

        if params.uris is not None:
            query_uris += params.uris
        if uris is not None:
            query_uris += uris

        if len(query_uris) > 0:

            recommendations = self.net.get_recommendations(tracks=[i.object_id for i in query_uris
                                                                   if i.object_type == Uri.ObjectType.track],
                                                           response_limit=params.recommendation_limit)
            if recommendations and len(recommendations) > 0:
                pass
            else:
                logger.error('error getting recommendations')

            return recommendations

        else:
            logger.error('no uris to get recommendations for')
