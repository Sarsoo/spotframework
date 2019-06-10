from .abstractprocessor import AbstractProcessor
import random


class Shuffle(AbstractProcessor):

    def process(self, tracks):
        random.shuffle(tracks)
        return tracks
