from abc import ABC, abstractmethod
from typing import List
from spotframework.model.track import Track


class AbstractProcessor(ABC):

    def __init__(self, names: List[str] = None):
        self.playlist_names = names

    def has_targets(self):
        if self.playlist_names:
            return True
        else:
            return False

    @abstractmethod
    def process(self, tracks: List[Track]):
        pass


class BatchSingleProcessor(AbstractProcessor, ABC):

    @staticmethod
    def process_single(track: Track):
        return track

    def process_batch(self, tracks: List[Track]):
        processed = []

        for track in tracks:
            processed_track = self.process_single(track)
            processed.append(processed_track)

        return processed

    def process(self, tracks: List[Track]):
        return [i for i in self.process_batch(tracks) if i]


class BatchSingleTypeAwareProcessor(BatchSingleProcessor, ABC):

    def __init__(self,
                 names: List[str] = None,
                 instance_check=None,
                 append_malformed: bool = True):
        super().__init__(names)
        self.instance_check = instance_check
        self.append_malformed = append_malformed

    def process(self, tracks: List[Track]):

        if self.instance_check:
            return_tracks = []
            malformed_tracks = []

            for track in tracks:

                if isinstance(track, self.instance_check):
                    return_tracks.append(track)
                else:
                    malformed_tracks.append(track)

            return_tracks = super().process(return_tracks)

            if self.append_malformed:
                return_tracks += malformed_tracks

            return return_tracks
        else:
            return tracks
