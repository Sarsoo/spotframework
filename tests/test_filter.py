import unittest
from unittest.mock import Mock, MagicMock, create_autospec

from dataclasses import fields

from util import create_dataclass_mock

from spotframework.model.track import SimplifiedTrack, TrackFull, PlaylistTrack, PlayedTrack, LibraryTrack
from spotframework.filter import get_track_objects

complex_track_types = [PlaylistTrack, PlayedTrack, LibraryTrack]

class TestFilterUtilFunctions(unittest.TestCase):

    def test_simple_track_for_no_track_attr(self):
        self.assertFalse('track' in (i.name for i in fields(SimplifiedTrack)))

    def test_high_level_types_for_track_attr(self):
        for class_type in complex_track_types:
            self.assertTrue('track' in (i.name for i in fields(class_type)),
                f'{class_type} does not have a track attribute')

    def test_get_tracks_for_simple_track(self):
        mock_track = create_dataclass_mock(SimplifiedTrack)

        self.assertIsInstance(mock_track, SimplifiedTrack)

        self.assertFalse(hasattr(mock_track, 'track'))

        [(item, item_two)] = get_track_objects([mock_track])
        
        self.assertEqual(item, mock_track)
        self.assertEqual(item_two, mock_track)

    def test_get_tracks_for_complex_track_types(self):
        for class_type in complex_track_types:
            mock_track = create_dataclass_mock(class_type)

            self.assertIsInstance(mock_track, class_type)

            self.assertTrue(hasattr(mock_track, 'track'), f'{class_type} does not have a track attr')
            
            [(item, item_two)] = get_track_objects([mock_track])
            
            self.assertEqual(item, mock_track.track)
            self.assertEqual(item_two, mock_track)

    def test_get_tracks_for_multiple_track_types(self):
        tracks = [create_dataclass_mock(class_type) for class_type in [SimplifiedTrack] + complex_track_types]

        self.assertFalse(hasattr(tracks[0], 'track'))
        for mock_track in tracks[1:]:
            self.assertTrue(hasattr(mock_track, 'track'), f'{mock_track.__class__} does not have a track attr')
        
        returned_tuples = list(get_track_objects(tracks))
        
        item, item_two = returned_tuples[0]
        self.assertEqual(item, tracks[0])
        self.assertEqual(item_two, tracks[0])
        for mock_track, (item, item_two) in list(zip(tracks, returned_tuples))[1:]:
            self.assertEqual(item, mock_track.track)
            self.assertEqual(item_two, mock_track)


if __name__ == '__main__':
    unittest.main()