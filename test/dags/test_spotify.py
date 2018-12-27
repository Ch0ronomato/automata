import unittest
from unittest.mock import Mock, call, patch, PropertyMock
from dags.integrations.spotify import SpotifyAPI

class TestSpotify(unittest.TestCase):
    def setUp(self):
        self.unit = SpotifyAPI()

    def test_playground(self):
        # self.unit.find_album_links([{'band': 'Coheed and Cambria', 'song': 'Far'}])
        self.unit.create_playlist(["spotify:album:1CMw0rLUVCNjvPQp7UKyhv"])

