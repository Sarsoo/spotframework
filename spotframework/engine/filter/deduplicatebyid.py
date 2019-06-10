from .abstractprocessor import AbstractProcessor


class DeduplicateByID(AbstractProcessor):

    def process(self, tracks):
        return_tracks = []

        for track in tracks:
            if track['track']['uri'] not in [i['track']['uri'] for i in return_tracks]:
                return_tracks.append(track)

        return return_tracks
