import unittest
from unittest.mock import Mock

from spotframework.model.uri import Uri
from spotframework.util.decorators import inject_uri

class TestInjectURI(unittest.TestCase):

    def test_one_uri(self):
        func = Mock()
        decorated = inject_uri(func, uris=False)
        
        result = decorated(uri="spotify:track:test")

        self.assertIsInstance(func.call_args.kwargs["uri"], Uri)
        func.assert_called_once()

    def test_uris(self):
        func = Mock()
        decorated = inject_uri(func, uri=False)

        result = decorated(uris=["spotify:track:test", 
                                 "spotify:album:test"])

        for arg in func.call_args.kwargs["uris"]:
            self.assertIsInstance(arg, Uri)
        func.assert_called_once()

    def test_uri_optional(self):
        func = Mock()
        decorated = inject_uri(func, uri_optional=True, uris=False)

        result = decorated()

        func.assert_called_once()
        

if __name__ == '__main__':
    unittest.main()