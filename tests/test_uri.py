import unittest

from spotframework.model.uri import Uri

class TestURI(unittest.TestCase):

    def test_input_not_string(self):
        with self.assertRaises(AttributeError):
            Uri(7)

    def test_start_spotify(self):
        with self.assertRaises(ValueError):
            # all uris start with spotify
            # spotify:track:3EHhS6B2qJWup1nqUVQy1H
            Uri("_potify:track:3EHhS6B2qJWup1nqUVQy1H")

    # test 5 component scenario or remove from source 

    def test_6_components_is_local_uri(self):
        with self.assertRaises(ValueError):
            # all uris start with spotify
            # spotify:local:{artist}:{album_title}:{track_title}:{duration_in_seconds}
            Uri("spotify:_ocal:{artist}:{album_title}:{track_title}:{duration_in_seconds}")

    def test_too_many_components(self):
        with self.assertRaises(ValueError):
            # all uris start with spotifys
            Uri("spotify:test:test:test:test:test:test")
    
    def test_equals(self):
        uri_one = Uri("spotify:track:test")
        uri_two = Uri("spotify:track:test")

        self.assertEqual(uri_one, uri_two)

    def test_equal_different_type(self):
        uri_one = Uri("spotify:track:test")
        uri_two = 7

        self.assertNotEqual(uri_one, uri_two)

    def test_equal_object_type(self):
        uri_one = Uri("spotify:album:test")
        uri_two = Uri("spotify:track:test")

        self.assertNotEqual(uri_one, uri_two)

    def test_equal_object_id(self):
        uri_one = Uri("spotify:track:test")
        uri_two = Uri("spotify:track:tester")

        self.assertNotEqual(uri_one, uri_two)

    def test_str(self):
        uri = Uri("spotify:track:test")

        self.assertEqual(str(uri), "spotify:track:test")

    def test_repr(self):
        uri = Uri("spotify:track:test")

        self.assertEqual(repr(uri), "URI: track / test")


if __name__ == '__main__':
    unittest.main()