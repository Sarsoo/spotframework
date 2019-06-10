import spotframework.log.log as log

import requests
import os

import spotframework.util.monthstrings as monthstrings
from spotframework.engine.filter.addedsince import AddedSince


class PlaylistEngine:

    def __init__(self, net):
        self.playlists = []
        self.net = net

    def load_user_playlists(self):
        self.playlists = self.net.getUserPlaylists()

    def append_user_playlists(self):
        self.playlists += self.net.getUserPlaylists()

    def get_playlist_tracks(self, playlist):
        log.log("pulling tracks for {}".format(playlist.name))
        playlist.tracks = self.net.getPlaylistTracks(playlist.playlistid)

    def make_playlist(self, playlist_parts, processors=[]):

        tracks = []

        for part in playlist_parts:

            play = next((i for i in self.playlists if i.name == part), None)

            if play is not None:

                if play.has_tracks() is False:
                    self.get_playlist_tracks(play)

                playlist_tracks = list(play.tracks)

                for processor in [i for i in processors if play.name in [j for j in i.playlist_names]]:
                    playlist_tracks = processor.process(playlist_tracks)

                tracks += [i for i in playlist_tracks if i['is_local'] is False]

            else:
                log.log("requested playlist {} not found".format(part))
                if 'SLACKHOOK' in os.environ:
                    requests.post(os.environ['SLACKHOOK'], json={"text": "spot playlists: {} not found".format(part)})

        for processor in [i for i in processors if len(i.playlist_names) <= 0]:
            tracks = processor.process(tracks)

        # print(tracks)
        return tracks

    def get_recent_playlist(self, boundary_date, recent_playlist_parts, processors=[]):
        this_month = monthstrings.get_this_month()
        last_month = monthstrings.get_last_month()

        datefilter = AddedSince(boundary_date, recent_playlist_parts)

        processors.append(datefilter)

        return self.make_playlist(recent_playlist_parts + [this_month, last_month], processors)

    def execute_playlist(self, tracks, playlist_id):
        self.net.replacePlaylistTracks(playlist_id, [i['track']['uri'] for i in tracks])

    def change_description(self, playlistparts, playlist_id):
        self.net.changePlaylistDetails(playlist_id, description=' / '.join(playlistparts))