import requests
import os
import logging

import spotframework.util.monthstrings as monthstrings
from spotframework.engine.processor.added import AddedSince

from typing import List, Optional
from spotframework.model.track import SpotifyTrack
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.net.network import Network
from spotframework.engine.processor.abstract import AbstractProcessor
from datetime import datetime
from requests.models import Response

logger = logging.getLogger(__name__)


class PlaylistEngine:

    def __init__(self, net: Network):
        self.playlists = []
        self.net = net

    def load_user_playlists(self) -> None:
        logger.info('loading')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists = playlists
        else:
            logger.error('error getting playlists')

    def append_user_playlists(self) -> None:
        logger.info('loading')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists += playlists
        else:
            logger.error('error getting playlists')

    def get_playlist_tracks(self,
                            playlist: SpotifyPlaylist) -> None:
        logger.info(f"pulling tracks for {playlist.name}")

        tracks = self.net.get_playlist_tracks(playlist.playlist_id)
        if tracks and len(tracks) > 0:
            playlist.tracks = tracks
        else:
            logger.error('error getting tracks')

    def load_playlist_tracks(self, name: str):
        playlist = next((i for i in self.playlists if i.name == name), None)
        if playlist is not None:
            self.get_playlist_tracks(playlist)
        else:
            logger.error(f'playlist {name} not found')

    def make_playlist(self,
                      playlist_parts: List[str],
                      processors: List[AbstractProcessor] = None,
                      include_recommendations: bool = False,
                      recommendation_limit: int = 10) -> List[SpotifyTrack]:

        if processors is None:
            processors = []

        tracks = []

        for part in playlist_parts:

            play = next((i for i in self.playlists if i.name == part), None)

            if play is not None:

                if play.has_tracks() is False:
                    self.get_playlist_tracks(play)

                playlist_tracks = list(play.tracks)

                for processor in [i for i in processors if i.has_targets()]:
                    if play.name in [i for i in processor.playlist_names]:
                        playlist_tracks = processor.process(playlist_tracks)

                tracks += [i for i in playlist_tracks if i.is_local is False]

            else:
                logger.warning(f"requested playlist {part} not found")
                if 'SLACKHOOK' in os.environ:
                    requests.post(os.environ['SLACKHOOK'], json={"text": f"spot playlists: {part} not found"})

        for processor in [i for i in processors if i.has_targets() is False]:
            tracks = processor.process(tracks)

        if include_recommendations:
            recommendations = self.net.get_recommendations(tracks=[i.spotify_id for i in tracks],
                                                           response_limit=recommendation_limit)
            if recommendations and len(recommendations) > 0:
                tracks += recommendations
            else:
                logger.error('error getting recommendations')

        return tracks

    def get_recent_playlist(self,
                            boundary_date: datetime,
                            recent_playlist_parts: List[str],
                            processors: List[AbstractProcessor] = None,
                            include_recommendations: bool = False,
                            recommendation_limit: int = 10,
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

        datefilter = AddedSince(boundary_date, recent_playlist_parts + month_playlists)

        processors.append(datefilter)

        return self.make_playlist(recent_playlist_parts + month_playlists,
                                  processors,
                                  include_recommendations=include_recommendations,
                                  recommendation_limit=recommendation_limit)

    def reorder_playlist_by_added_date(self,
                                       name: str = None,
                                       playlistid: str = None,
                                       reverse: bool = False):
        if name is None and playlistid is None:
            logger.error('no playlist name or id provided')
            raise ValueError('no playlist name or id provided')

        if name:
            playlist = next((i for i in self.playlists if i.name == name), None)
        else:
            playlist = next((i for i in self.playlists if i.spotify_id == playlistid), None)

        if playlist is None:
            logger.error('playlist not found')
            return None

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

            self.net.reorder_playlist_tracks(playlist.playlist_id,
                                             i + tracks_to_sort.index(counter_track),
                                             1, i)
            tracks_to_sort.remove(counter_track)

    def execute_playlist(self,
                         tracks: List[SpotifyTrack],
                         playlist_id: str) -> Optional[Response]:

        resp = self.net.replace_playlist_tracks(playlist_id, [i.uri for i in tracks])
        if resp:
            return resp
        else:
            logger.error('error executing')
            return None

    def change_description(self,
                           playlistparts: List[str],
                           playlist_id: str,
                           overwrite: bool = None,
                           suffix: str = None) -> Optional[Response]:

        if overwrite:
            string = overwrite
        else:
            string = ' / '.join(playlistparts)

        if suffix:
            string += f' - {str(suffix)}'

        resp = self.net.change_playlist_details(playlist_id, description=string)
        if resp:
            return resp
        else:
            logger.error('error changing description')
