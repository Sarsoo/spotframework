from spotframework.engine.processor.abstract import BatchSingleProcessor, BatchSingleTypeAwareProcessor
from typing import List
import logging
from spotframework.model.track import Track, SpotifyTrack
from spotframework.model.uri import Uri

logger = logging.getLogger(__name__)


class DeduplicateByID(BatchSingleTypeAwareProcessor):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 append_malformed: bool = True):
        super().__init__(names=names,
                         uris=uris,
                         instance_check=SpotifyTrack,
                         append_malformed=append_malformed)

    def process_batch(self, tracks: List[SpotifyTrack]) -> List[SpotifyTrack]:
        return_tracks = []

        for track in tracks:
            if track.uri not in [i.uri for i in return_tracks]:
                return_tracks.append(track)

        return return_tracks


class DeduplicateByName(BatchSingleProcessor):

    def process_batch(self, tracks: List[Track]) -> List[Track]:
        return_tracks = []

        for to_check in tracks:
            to_check_artists = [i.name.lower() for i in to_check.artists]

            for index, _track in enumerate(return_tracks):
                if to_check.name.lower() == _track.name.lower():
                    
                    _track_artists = [i.name.lower() for i in _track.artists]
                    if all((i in _track_artists for i in to_check_artists)):  # CHECK ARTISTS MATCH

                        # CHECK ALBUM TYPE, PREFER ALBUMS OVER SINGLES ETC
                        if to_check.album.album_type.value > _track.album.album_type.value:
                            logger.debug(f'better track source found, {to_check} ({to_check.album.album_type}) '
                                         f'> {_track} ({_track.album.album_type})')
                            return_tracks[index] = to_check  # REPLACE
                        break  # FOUND, ESCAPE
            else:
                return_tracks.append(to_check)  # NOT FOUND, ADD TO RETURN

        return return_tracks
