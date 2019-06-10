from abc import ABC, abstractmethod


class AbstractProcessor(ABC):

    def __init__(self, names=[]):
        self.playlist_names = names

    @abstractmethod
    def process(self, tracks):
        pass
