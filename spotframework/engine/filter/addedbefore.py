from .abstractprocessor import AbstractProcessor
import datetime


class AddedBefore(AbstractProcessor):

    def __init__(self, boundary, names=[]):
        self.playlist_names = names
        self.boundary = boundary

    def check_date(self, track):
        added_at = datetime.datetime.fromisoformat(track['added_at'].replace('T', ' ').replace('Z', ''))

        return added_at < self.boundary

    def process(self, tracks):
        return [i for i in tracks if self.check_date(i)]
