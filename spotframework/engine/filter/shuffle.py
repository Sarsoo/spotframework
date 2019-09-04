from .abstract import AbstractProcessor
import random
from typing import List
from spotframework.model.track import Track


class Shuffle(AbstractProcessor):

    def process(self, tracks: List[Track]):
        random.shuffle(tracks)
        return tracks


class RandomSample(Shuffle):

    def __init__(self,
                 sample_size: int,
                 names: List[str] = None):
        super().__init__(names)
        self.sample_size = sample_size

    def process(self, tracks: List[Track]):
        return super().process(tracks)[:self.sample_size]
