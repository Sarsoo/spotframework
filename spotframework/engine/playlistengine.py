import requests
import os
import logging

import spotframework.util.monthstrings as monthstrings
from spotframework.engine.filter.added import AddedSince

from typing import List
from spotframework.model.track import SpotifyTrack
from spotframework.model.playlist import SpotifyPlaylist
from spotframework.net.network import Network
from spotframework.engine.filter.abstract import AbstractProcessor
from datetime import datetime

logger = logging.getLogger(__name__)


class PlaylistEngine:

    def __init__(self, net: Network):
        self.playlists = []
        self.net = net

    def load_user_playlists(self):
        logger.info('loading')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists = playlists
        else:
            logger.error('error getting playlists')

    def append_user_playlists(self):
        logger.info('loading')

        playlists = self.net.get_playlists()
        if playlists and len(playlists) > 0:
            self.playlists += playlists
        else:
            logger.error('error getting playlists')

    def get_playlist_tracks(self,
                            playlist: SpotifyPlaylist):
        logger.info(f"pulling tracks for {playlist.name}")

        tracks = self.net.get_playlist_tracks(playlist.playlist_id)
        if tracks and len(tracks) > 0:
            playlist.tracks = tracks
        else:
            logger.error('error getting tracks')

    def make_playlist(self,
                      playlist_parts: List[str],
                      processors: List[AbstractProcessor] = None,
                      include_recommendations: bool = False,
                      recommendation_limit: int = 10):

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
                            add_last_month: bool = False):

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

    def execute_playlist(self,
                         tracks: List[SpotifyTrack],
                         playlist_id: str):

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
                           suffix: str = None):

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
