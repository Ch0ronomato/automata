import unittest
from unittest.mock import Mock, call, patch, PropertyMock
from dags.integrations.spotify import SpotifyAPI

class TestSpotify(unittest.TestCase):
    def setUp(self):
        self.unit = SpotifyAPI()

    def test_auth_works(self):
        pass
