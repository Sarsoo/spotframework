from .abstract import AbstractProcessor
import random
from typing import List
from spotframework.model.track import Track
from spotframework.model.uri import Uri


class Shuffle(AbstractProcessor):

    def process(self, tracks: List[Track]) -> List[Track]:
        random.shuffle(tracks)
        return tracks


class RandomSample(Shuffle):

    def __init__(self,
                 sample_size: int,
                 names: List[str] = None,
                 uris: List[Uri] = None):
        super().__init__(names=names, uris=uris)
        self.sample_size = sample_size

    def process(self, tracks: List[Track]) -> List[Track]:
        return super().process(tracks)[:self.sample_size]
