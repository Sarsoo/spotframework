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


class AbstractTestFilter(AbstractProcessor, ABC):

    def __init__(self,
                 names: List[str] = None,
                 keep_failed: bool = True):
        super().__init__(names)
        self.keep_failed = keep_failed

    @abstractmethod
    def logic_test(self, track: Track):
        pass

    def process(self, tracks: List[Track]):

        return_tracks = []
        malformed_tracks = []

        for track in tracks:
            if self.logic_test(track):
                return_tracks.append(track)
            else:
                malformed_tracks.append(track)
        if self.keep_failed:
            return_tracks += malformed_tracks

        return return_tracks
