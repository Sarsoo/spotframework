from abc import ABC, abstractmethod
from typing import List
from spotframework.model.track import SimplifiedTrack
from spotframework.model.uri import Uri


class AbstractProcessor(ABC):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None):
        self.playlist_names = names
        self.playlist_uris = uris

    def has_targets(self) -> bool:
        if self.playlist_names or self.playlist_uris:
            return True
        else:
            return False

    @abstractmethod
    def process(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:
        pass


class BatchSingleProcessor(AbstractProcessor, ABC):

    @staticmethod
    def process_single(track: SimplifiedTrack) -> SimplifiedTrack:
        return track

    def process_batch(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:
        return [self.process_single(track) for track in tracks]

    def process(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:
        return [i for i in self.process_batch(tracks) if i is not None]


class BatchSingleTypeAwareProcessor(BatchSingleProcessor, ABC):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 instance_check=None,
                 append_malformed: bool = True):
        super().__init__(names, uris)
        if isinstance(instance_check, list):
            self.instance_check = instance_check
        else:
            self.instance_check = [instance_check]
        self.append_malformed = append_malformed

    def process(self, tracks: List[SimplifiedTrack]) -> List[SimplifiedTrack]:

        if self.instance_check:
            return_tracks = []
            malformed_tracks = []

            for track in tracks:

                if any(isinstance(track, i) for i in self.instance_check):
                    return_tracks.append(track)
                else:
                    malformed_tracks.append(track)

            return_tracks = super().process(return_tracks)

            if self.append_malformed:
                return_tracks += malformed_tracks

            return return_tracks
        else:
            return tracks
