from spotframework.engine.processor.abstract import BatchSingleProcessor
from abc import ABC, abstractmethod
from typing import List
from spotframework.model.track import TrackFull
from spotframework.model.uri import Uri


class AudioFeaturesProcessor(BatchSingleProcessor, ABC):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 append_malformed: bool = True):
        super().__init__(names=names,
                         uris=uris)
        self.append_malformed = append_malformed

    def process(self, tracks: List[TrackFull]) -> List[TrackFull]:

        return_tracks = []
        malformed_tracks = []

        for track in tracks:

            if isinstance(track, TrackFull) and track.audio_features is not None:
                return_tracks.append(track)
            else:
                malformed_tracks.append(track)

        return_tracks = super().process(return_tracks)

        if self.append_malformed:
            return_tracks += malformed_tracks

        return return_tracks


class FloatFilter(AudioFeaturesProcessor, ABC):

    def __init__(self,
                 names: List[str] = None,
                 uris: List[Uri] = None,
                 append_malformed: bool = True,
                 boundary: float = None,
                 greater_than: bool = True):
        super().__init__(names=names,
                         uris=uris,
                         append_malformed=append_malformed)
        self.boundary = boundary
        self.greater_than = greater_than

    @abstractmethod
    def get_variable_value(self, track: TrackFull) -> float:
        pass

    def process_single(self, track: TrackFull):
        if self.greater_than:
            if self.get_variable_value(track) > self.boundary:
                return track
            else:
                return None
        else:
            if self.get_variable_value(track) < self.boundary:
                return track
            else:
                return None


class EnergyFilter(FloatFilter):
    def get_variable_value(self, track: TrackFull) -> float:
        return track.audio_features.energy


class ValenceFilter(FloatFilter):
    def get_variable_value(self, track: TrackFull) -> float:
        return track.audio_features.valence


class TempoFilter(FloatFilter):
    def get_variable_value(self, track: TrackFull) -> float:
        return track.audio_features.tempo


class DanceabilityFilter(FloatFilter):
    def get_variable_value(self, track: TrackFull) -> float:
        return track.audio_features.danceability


class AcousticnessFilter(FloatFilter):
    def get_variable_value(self, track: TrackFull) -> float:
        return track.audio_features.acousticness
