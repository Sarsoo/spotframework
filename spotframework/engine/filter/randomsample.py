from .abstractprocessor import AbstractProcessor

import random


class RandomSample(AbstractProcessor):

    def __init__(self, sample_size, names=[]):
        super().__init__(names)
        self.sample_size = sample_size

    def process(self, tracks):

        return_tracks = list(tracks)
        random.shuffle(return_tracks)

        return return_tracks[:self.sample_size]
