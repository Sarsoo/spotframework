from .abstractprocessor import AbstractProcessor


class SortReverseReleaseDate(AbstractProcessor):

    def process(self, tracks):
        tracks.sort(key=lambda x: x['track']['album']['release_date'], reverse=True)
        return tracks
