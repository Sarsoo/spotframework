import unittest
from unittest.mock import Mock, MagicMock, create_autospec

from dataclasses import fields

import datetime

from util import create_dataclass_mock

from spotframework.model.track import SimplifiedTrack, TrackFull, PlaylistTrack, PlayedTrack, LibraryTrack
from spotframework.model.album import SimplifiedAlbum
from spotframework.model.artist import SimplifiedArtist
from spotframework.model.uri import Uri
from spotframework.filter import get_track_objects, remove_local
from spotframework.filter.added import added_after, added_before
from spotframework.filter.deduplicate import deduplicate_by_id, deduplicate_by_name
from spotframework.filter.sort import sort_by_popularity, sort_by_release_date, sort_by_added_date, sort_artist_album_track_number

complex_track_types = [PlaylistTrack, PlayedTrack, LibraryTrack]

class TestFilterGetTrackObjects(unittest.TestCase):

    def test_simple_track_for_no_track_attr(self):
        """
        Test SimplifiedTrack for the track attribute (it shouldn't have it)
        """
        self.assertFalse('track' in (i.name for i in fields(SimplifiedTrack)))

    def test_high_level_types_for_track_attr(self):
        """
        Test higher level track types for the track attribute (they should have it)
        """
        for class_type in complex_track_types:
            self.assertTrue('track' in (i.name for i in fields(class_type)),
                f'{class_type} does not have a track attribute')

    def test_get_tracks_for_simple_track(self):
        """
        Check that the same object is returned twice if it's a simple track
        """
        mock_track = create_dataclass_mock(SimplifiedTrack)

        self.assertIsInstance(mock_track, SimplifiedTrack)

        self.assertFalse(hasattr(mock_track, 'track'))

        [(item, item_two)] = get_track_objects([mock_track])
        
        self.assertEqual(item, mock_track)
        self.assertEqual(item_two, mock_track)

    @unittest.skip("inner tracks aren't passing new type check because they're mocks")
    def test_get_tracks_for_complex_track_types(self):
        """
        Check that the nested SimplifiedTrack object is returned for each complex track type
        """
        for class_type in complex_track_types:
            mock_track = create_dataclass_mock(class_type)

            self.assertIsInstance(mock_track, class_type)

            self.assertTrue(hasattr(mock_track, 'track'), f'{class_type} does not have a track attr')
            
            [(item, item_two)] = get_track_objects([mock_track])
            
            self.assertEqual(item, mock_track.track)
            self.assertEqual(item_two, mock_track)

    @unittest.skip("inner tracks aren't passing new type check because they're mocks")
    def test_get_tracks_for_multiple_track_types(self):
        """
        Test correct objects are returned when using all track types together
        """
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

class TestFilterRemoveLocal(unittest.TestCase):

    def test_simple_track_for_is_local_attr(self):
        """
        Check SimplifiedTrack for is_local attr (it should have it)
        """
        self.assertTrue('is_local' in (i.name for i in fields(SimplifiedTrack)))

    def test_return_not_local(self):
        """
        Check that track is returned if it is not local (a live service track)
        """
        mock_track = create_dataclass_mock(SimplifiedTrack)
        mock_track.is_local = False

        self.assertTrue(hasattr(mock_track, 'is_local'))

        [returned_track] = remove_local([mock_track], include_malformed=False)

        self.assertEqual(mock_track, returned_track)
    
    def test_dont_return_local(self):
        """
        Check that local tracks are filtered out
        """
        mock_track = create_dataclass_mock(SimplifiedTrack)
        mock_track.is_local = True

        self.assertTrue(hasattr(mock_track, 'is_local'))

        returned_tracks = list(remove_local([mock_track], include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)

    def test_return_from_multiple(self):
        """
        Check right tracks are filtered out when provided together
        """
        mock_track_one = create_dataclass_mock(SimplifiedTrack)
        mock_track_one.is_local = True

        mock_track_two = create_dataclass_mock(SimplifiedTrack)
        mock_track_two.is_local = False

        self.assertTrue(hasattr(mock_track_one, 'is_local'))
        self.assertTrue(hasattr(mock_track_two, 'is_local'))

        returned_tracks = list(remove_local([mock_track_one, mock_track_two], include_malformed=False))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track_two)

    def test_include_malformed(self):
        """
        Check that unexpected types are returned if using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'is_local'))

        returned_tracks = list(remove_local([mock_track], include_malformed=True))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_no_include_malformed(self):
        """
        Check that unexpected types are not returned if not using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'is_local'))

        returned_tracks = list(remove_local([mock_track], include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)

class TestFilterAdded(unittest.TestCase):

    def test_playable_types_for_added_at_attr(self):
        """
        Test playable tracks for added_at attr
        """
        for class_type in [PlaylistTrack, LibraryTrack]:
            self.assertTrue('added_at' in (i.name for i in fields(class_type)),
                f'{class_type} does not have an added_at attribute')

    def test_nonplayable_types_for_no_added_at_attr(self):
        """
        Test unplayable tracks for added_at attr
        """
        for class_type in [SimplifiedTrack, PlayedTrack]:
            self.assertFalse('added_at' in (i.name for i in fields(class_type)),
                f'{class_type} has an added_at attribute')

    ### ADDED_AFTER ###

    def test_added_after_filtered(self):
        """
        Test added_after correctly filters old tracks
        """
        mock_track = create_dataclass_mock(PlaylistTrack)
        mock_track.added_at = datetime.datetime(year=2018, month=1, day=1)

        self.assertTrue(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=2)

        returned_tracks = list(added_after([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)

    def test_added_after_returned(self):
        """
        Test added_after correctly returns newer tracks
        """
        mock_track = create_dataclass_mock(PlaylistTrack)
        mock_track.added_at = datetime.datetime(year=2018, month=1, day=2)

        self.assertTrue(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_after([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_after_include_malformed(self):
        """
        Check that unexpected types are returned if using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_after([mock_track], boundary=boundary, include_malformed=True))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_after_no_include_malformed(self):
        """
        Check that unexpected types are not returned if not using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_after([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)
    
    ### ADDED_BEFORE ###

    def test_added_before_filtered(self):
        """
        Test added_before correctly filters new tracks
        """
        mock_track = create_dataclass_mock(PlaylistTrack)
        mock_track.added_at = datetime.datetime(year=2018, month=1, day=2)

        self.assertTrue(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_before([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)

    def test_added_before_returned(self):
        """
        Test added_before correctly returns older tracks
        """
        mock_track = create_dataclass_mock(PlaylistTrack)
        mock_track.added_at = datetime.datetime(year=2018, month=1, day=1)

        self.assertTrue(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=2)

        returned_tracks = list(added_before([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_before_include_malformed(self):
        """
        Check that unexpected types are returned if using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_before([mock_track], boundary=boundary, include_malformed=True))

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_before_no_include_malformed(self):
        """
        Check that unexpected types are not returned if not using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'added_at'))

        boundary = datetime.datetime(year=2018, month=1, day=1)

        returned_tracks = list(added_before([mock_track], boundary=boundary, include_malformed=False))

        self.assertTrue(len(returned_tracks) == 0)

class TestFilterDeduplicate(unittest.TestCase):

    ### DEDUPLICATE BY URI ###

    def test_simple_track_for_uri_attr(self):
        """
        Test SimplifiedTrack for the uri attribute (it should have it)
        """
        self.assertTrue('uri' in (i.name for i in fields(SimplifiedTrack)))

    def test_high_level_types_for_no_uri_attr(self):
        """
        Test higher level track types for the uri attribute (they shouldn't have it)
        """
        for class_type in complex_track_types:
            self.assertFalse('uri' in (i.name for i in fields(class_type)),
                f'{class_type} does not have a track attribute')

    def test_by_uri_with_one_track(self):
        """
        Test deduping my id returns one track when provided one track
        """
        mock_track = create_dataclass_mock(SimplifiedTrack)
        mock_track.uri = Uri('spotify:track:1')

        self.assertTrue(hasattr(mock_track, 'uri'))
        self.assertIsInstance(mock_track.uri, Uri)

        returned_tracks = deduplicate_by_id([mock_track], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(mock_track, returned_tracks[0])

    def test_by_uri_with_two_different_tracks(self):
        """
        Test deduping my id returns two distinct tracks
        """
        mock_track_one = create_dataclass_mock(SimplifiedTrack)
        mock_track_one.uri = Uri('spotify:track:1')

        mock_track_two = create_dataclass_mock(SimplifiedTrack)
        mock_track_two.uri = Uri('spotify:track:2')

        self.assertTrue(hasattr(mock_track_one, 'uri'))
        self.assertTrue(hasattr(mock_track_two, 'uri'))
        self.assertIsInstance(mock_track_one.uri, Uri)
        self.assertIsInstance(mock_track_two.uri, Uri)

        returned_tracks = deduplicate_by_id([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_uri_with_repeated_tracks(self):
        """
        Test deduping my id returns two distinct tracks when one duplicate is provided
        """
        mock_track_one = create_dataclass_mock(SimplifiedTrack)
        mock_track_one.uri = Uri('spotify:track:1')

        mock_track_two = create_dataclass_mock(SimplifiedTrack)
        mock_track_two.uri = Uri('spotify:track:2')

        mock_track_three = create_dataclass_mock(SimplifiedTrack)
        mock_track_three.uri = Uri('spotify:track:1')

        for track in [mock_track_one, mock_track_two, mock_track_three]:
            self.assertTrue(hasattr(track, 'uri'))
            self.assertIsInstance(track.uri, Uri)

        returned_tracks = deduplicate_by_id([mock_track_one, mock_track_two, mock_track_three], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_uri_with_multiple_repeated_tracks(self):
        """
        Test deduping my id returns two distinct tracks when one duplicate is provided
        """
        mock_track_one = create_dataclass_mock(SimplifiedTrack)
        mock_track_one.uri = Uri('spotify:track:1')

        mock_track_two = create_dataclass_mock(SimplifiedTrack)
        mock_track_two.uri = Uri('spotify:track:2')

        mock_track_three = create_dataclass_mock(SimplifiedTrack)
        mock_track_three.uri = Uri('spotify:track:1')

        mock_track_four = create_dataclass_mock(SimplifiedTrack)
        mock_track_four.uri = Uri('spotify:track:2')

        for track in [mock_track_one, mock_track_two, mock_track_three, mock_track_four]:
            self.assertTrue(hasattr(track, 'uri'))
            self.assertIsInstance(track.uri, Uri)

        returned_tracks = deduplicate_by_id([mock_track_one, mock_track_two, mock_track_three, mock_track_four], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_uri_include_malformed(self):
        """
        Check that unexpected types are returned if using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'uri'))

        returned_tracks = deduplicate_by_id([mock_track], include_malformed=True)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_by_uri_no_include_malformed(self):
        """
        Check that unexpected types are not returned if not using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertFalse(hasattr(mock_track, 'uri'))

        returned_tracks = deduplicate_by_id([mock_track], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 0)

    ### DEDUPLICATE BY NAME ###

    def test_by_name_with_one_track(self):
        """
        Test deduping my name returns one track when provided one track
        """
        mock_track = create_dataclass_mock(TrackFull)
        mock_track.name = 'test'
        mock_track.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track.artists[0].name = 'test_artist'

        self.assertIsInstance(mock_track, TrackFull)

        returned_tracks = deduplicate_by_name([mock_track], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(mock_track, returned_tracks[0])

    def test_by_name_with_two_different_tracks(self):
        """
        Test deduping my name returns two distinct tracks
        """
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test_two'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_name_with_repeated_tracks(self):
        """
        Test deduping my name doesn't return duplicated
        """
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.album.album_type.value = 0 # for album type check

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test_two'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.name = 'test'
        mock_track_three.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.artists[0].name = 'test_artist'
        mock_track_three.album.album_type.value = 0 # for album type check

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three]]

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two, mock_track_three], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_name_with_multiple_repeated_tracks(self):
        """
        Test deduping my name doesn't return duplicated
        """
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.album.album_type.value = 0 # for album type check

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test_two'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'
        mock_track_two.album.album_type.value = 0 # for album type check

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.name = 'tEst'
        mock_track_three.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.artists[0].name = 'test_arTISt'
        mock_track_three.album.album_type.value = 0 # for album type check

        mock_track_four = create_dataclass_mock(TrackFull)
        mock_track_four.name = 'TEST_TWO'
        mock_track_four.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_four.artists[0].name = 'test_artist'
        mock_track_four.album.album_type.value = 0 # for album type check

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three, mock_track_four]]

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two, mock_track_three, mock_track_four], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_name_with_multiple_artists(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist), create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.artists[1].name = 'test_artist_two'
        mock_track_one.album.album_type.value = 0 # for album type check

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist), create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[1].name = 'test_artist' # different order as well just for sure
        mock_track_two.artists[0].name = 'test_artist_two'
        mock_track_two.album.album_type.value = 0 # for album type check

        self.assertIsInstance(mock_track_one, TrackFull)
        self.assertIsInstance(mock_track_two, TrackFull)

        self.assertEqual(mock_track_one.name.lower(), mock_track_two.name.lower())
        self.assertEqual(mock_track_one.artists[0].name.lower(), mock_track_two.artists[1].name.lower())
        self.assertEqual(mock_track_one.artists[1].name.lower(), mock_track_two.artists[0].name.lower())
        # ^ different order for checking as well

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 1, f'{len(returned_tracks)} returned')
        self.assertEqual(mock_track_one, returned_tracks[0])

    def test_by_name_with_multiple_different_artists(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist), create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.artists[1].name = 'test_artist_two'
        mock_track_one.album.album_type.value = 0 # for album type check

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist), create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'
        mock_track_one.artists[1].name = 'test_artist_three'
        mock_track_two.album.album_type.value = 0 # for album type check

        self.assertIsInstance(mock_track_one, TrackFull)
        self.assertIsInstance(mock_track_two, TrackFull)

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_by_name_with_album_type_pick(self):
        """
        Test that highest album type is selected
        """
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.album.album_type = SimplifiedAlbum.Type.single

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'
        mock_track_two.album.album_type = SimplifiedAlbum.Type.album

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(mock_track_two, returned_tracks[0])

    def test_by_name_with_album_type_pick_alternate(self):
        """
        Test that highest album type is selected
        """
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.name = 'test'
        mock_track_one.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.artists[0].name = 'test_artist'
        mock_track_one.album.album_type = SimplifiedAlbum.Type.compilation

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.name = 'test'
        mock_track_two.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.artists[0].name = 'test_artist'
        mock_track_two.album.album_type = SimplifiedAlbum.Type.single

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = deduplicate_by_name([mock_track_one, mock_track_two], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(mock_track_one, returned_tracks[0])

    def test_by_name_include_malformed(self):
        """
        Check that unexpected types are returned if using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertNotIsInstance(mock_track, TrackFull)

        returned_tracks = deduplicate_by_name([mock_track], include_malformed=True)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertEqual(returned_tracks[0], mock_track)

    def test_by_name_no_include_malformed(self):
        """
        Check that unexpected types are not returned if not using include_malformed
        """
        mock_track = Mock(spec_set=True)

        self.assertNotIsInstance(mock_track, TrackFull)

        returned_tracks = deduplicate_by_name([mock_track], include_malformed=False)

        self.assertTrue(len(returned_tracks) == 0)

class TestFilterSort(unittest.TestCase):

    ### POPULARITY ###

    def test_popularity(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.popularity = 50

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.popularity = 60

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = sort_by_popularity([mock_track_one, mock_track_two], reverse=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    def test_popularity_alternate(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.popularity = 60

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.popularity = 50

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = sort_by_popularity([mock_track_one, mock_track_two], reverse=False)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_two, returned_tracks[0])
        self.assertEqual(mock_track_one, returned_tracks[1])

    def test_popularity_reverse(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.popularity = 60

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.popularity = 50

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = sort_by_popularity([mock_track_one, mock_track_two], reverse=True)

        self.assertTrue(len(returned_tracks) == 2)
        self.assertEqual(mock_track_one, returned_tracks[0])
        self.assertEqual(mock_track_two, returned_tracks[1])

    ### ARTIST/ALBUM/TRACK ###

    def test_artist_album_track_number_by_artist(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.disc_number = 1
        mock_track_one.track_number = 1
        mock_track_one.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.album.name = 'album'
        mock_track_one.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.album.artists[0].name = 'bbb artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.disc_number = 1
        mock_track_two.track_number = 1
        mock_track_two.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_two.album.name = 'album'
        mock_track_two.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.album.artists[0].name = 'aaa artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two]]

        returned_tracks = sort_artist_album_track_number([mock_track_one, mock_track_two])

        self.assertTrue(len(returned_tracks) == 2)
        # tuples returned by default, subscript again
        self.assertEqual(mock_track_two, returned_tracks[0][1])
        self.assertEqual(mock_track_one, returned_tracks[1][1])

    def test_artist_album_track_number_by_artist_alternate(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.disc_number = 1
        mock_track_one.track_number = 1
        mock_track_one.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.album.name = 'album'
        mock_track_one.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.album.artists[0].name = 'bbb artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.disc_number = 1
        mock_track_two.track_number = 1
        mock_track_two.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_two.album.name = 'album'
        mock_track_two.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.album.artists[0].name = 'ccc artist'

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.disc_number = 1
        mock_track_three.track_number = 1
        mock_track_three.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_three.album.name = 'album'
        mock_track_three.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.album.artists[0].name = 'aaa artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three]]

        returned_tracks = sort_artist_album_track_number([mock_track_one, mock_track_two, mock_track_three])

        self.assertTrue(len(returned_tracks) == 3)
        # tuples returned by default, subscript again
        self.assertEqual(mock_track_three, returned_tracks[0][1])
        self.assertEqual(mock_track_one, returned_tracks[1][1])
        self.assertEqual(mock_track_two, returned_tracks[2][1])

    def test_artist_album_track_number_by_album(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.disc_number = 1
        mock_track_one.track_number = 1
        mock_track_one.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.album.name = 'album'
        mock_track_one.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.album.artists[0].name = 'bbb artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.disc_number = 1
        mock_track_two.track_number = 1
        mock_track_two.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_two.album.name = 'aaa album'
        mock_track_two.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.album.artists[0].name = 'aaa artist'

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.disc_number = 1
        mock_track_three.track_number = 1
        mock_track_three.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_three.album.name = 'bbb album'
        mock_track_three.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.album.artists[0].name = 'aaa artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three]]

        returned_tracks = sort_artist_album_track_number([mock_track_one, mock_track_two, mock_track_three])

        self.assertTrue(len(returned_tracks) == 3)
        # tuples returned by default, subscript again
        self.assertEqual(mock_track_two, returned_tracks[0][1])
        self.assertEqual(mock_track_three, returned_tracks[1][1])
        self.assertEqual(mock_track_one, returned_tracks[2][1])

    def test_artist_album_track_number_by_disc(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.disc_number = 1
        mock_track_one.track_number = 1
        mock_track_one.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.album.name = 'album'
        mock_track_one.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.album.artists[0].name = 'bbb artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.disc_number = 2
        mock_track_two.track_number = 1
        mock_track_two.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_two.album.name = 'aaa album'
        mock_track_two.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.album.artists[0].name = 'aaa artist'

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.disc_number = 1
        mock_track_three.track_number = 1
        mock_track_three.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_three.album.name = 'aaa album'
        mock_track_three.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.album.artists[0].name = 'aaa artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three]]

        returned_tracks = sort_artist_album_track_number([mock_track_one, mock_track_two, mock_track_three])

        self.assertTrue(len(returned_tracks) == 3)
        # tuples returned by default, subscript again
        self.assertEqual(mock_track_three, returned_tracks[0][1])
        self.assertEqual(mock_track_two, returned_tracks[1][1])
        self.assertEqual(mock_track_one, returned_tracks[2][1])

    def test_artist_album_track_number_by_track(self):
        mock_track_one = create_dataclass_mock(TrackFull)
        mock_track_one.disc_number = 1
        mock_track_one.track_number = 1
        mock_track_one.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.album.name = 'album'
        mock_track_one.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.album.artists[0].name = 'bbb artist'

        mock_track_two = create_dataclass_mock(TrackFull)
        mock_track_two.disc_number = 1
        mock_track_two.track_number = 2
        mock_track_two.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_two.album.name = 'aaa album'
        mock_track_two.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_two.album.artists[0].name = 'aaa artist'

        mock_track_three = create_dataclass_mock(TrackFull)
        mock_track_three.disc_number = 1
        mock_track_three.track_number = 1
        mock_track_three.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_three.album.name = 'aaa album'
        mock_track_three.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_three.album.artists[0].name = 'aaa artist'

        [self.assertIsInstance(i, TrackFull) for i in [mock_track_one, mock_track_two, mock_track_three]]

        returned_tracks = sort_artist_album_track_number([mock_track_one, mock_track_two, mock_track_three])

        self.assertTrue(len(returned_tracks) == 3)
        # tuples returned by default, subscript again
        self.assertEqual(mock_track_three, returned_tracks[0][1])
        self.assertEqual(mock_track_two, returned_tracks[1][1])
        self.assertEqual(mock_track_one, returned_tracks[2][1])

    def test_artist_album_track_number_inner_tracks_only(self):
        mock_track_one = create_dataclass_mock(PlaylistTrack)
        mock_track_one.track = create_dataclass_mock(SimplifiedTrack)
        mock_track_one.track.disc_number = 1
        mock_track_one.track.track_number = 1
        mock_track_one.track.album = create_dataclass_mock(SimplifiedAlbum)
        mock_track_one.track.album.name = 'album'
        mock_track_one.track.album.artists = [create_dataclass_mock(SimplifiedArtist)]
        mock_track_one.track.album.artists[0].name = 'artist'

        self.assertNotIsInstance(mock_track_one, SimplifiedTrack)
        self.assertIsInstance(mock_track_one.track, SimplifiedTrack)

        returned_tracks = sort_artist_album_track_number([mock_track_one], inner_tracks_only=True)

        self.assertTrue(len(returned_tracks) == 1)
        self.assertIsInstance(returned_tracks[0], SimplifiedTrack)
        self.assertEqual(mock_track_one.track, returned_tracks[0])


if __name__ == '__main__':
    unittest.main()