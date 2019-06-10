from .abstractprocessor import AbstractProcessor


class DeduplicateByName(AbstractProcessor):

    def process(self, tracks):
        return_tracks = []

        for to_check in tracks:

            for cache_track in return_tracks:
                if to_check['track']['name'].lower() == cache_track['track']['name'].lower():
                    if to_check['track']['artists'][0]['name'].lower() \
                            == cache_track['track']['artists'][0]['name'].lower():
                        break
            else:
                return_tracks.append(to_check)

        return return_tracks
