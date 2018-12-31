import unittest
from unittest.mock import Mock, call, patch, PropertyMock
from dags.integrations.spotify import SpotifyAPI

class TestSpotify(unittest.TestCase):
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def setUp(self, _):
        self.unit = SpotifyAPI()

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_find_album_matches_links_for_tracks_items_with_band_song_pair(self, auth_mock, spotify_mock):
        mock_response = """{
            "tracks": {
                "items": [{
                    "name": "Some Song",
                    "album": {
                        "id": "12345",
                        "release_date": "2018-01-01",
                        "album_type": "album"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                }]
            }
        }
        """
        import json
        spotify_mock().search = Mock(name="search mock", return_value=json.loads(mock_response))
        api = SpotifyAPI()
        self.assertEqual(api.find_album_links([{"band": "Some Artist", "song": "Some Song"}]), ["12345"])

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_find_album_links_picks_first_release_date_for_ambiguity(self, auth_mock, spotify_mock):
        mock_response= """{
            "tracks": {
                "items": [{
                    "name": "Some Song",
                    "album": {
                        "id": "12345",
                        "album_type": "album",
                        "release_date": "2018-01-01",
                        "release_date_precision": "day"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                },{
                    "name": "Some Song",
                    "album": {
                        "id": "2345",
                        "release_date": "2019-01-01",
                        "album_type": "album",
                        "release_date_precision": "day"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                }]
            }
        }
        """
        import json
        spotify_mock().search = Mock(name="search mock", return_value=json.loads(mock_response))
        api = SpotifyAPI()
        self.assertEqual(api.find_album_links([{"band": "Some Artist", "song": "Some Song"}]), ["12345"])
    
    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_find_album_links_accounts_for_release_date_precision(self, _, spotify_mock):
        mock_response= """{
            "tracks": {
                "items": [{
                    "name": "Some Song",
                    "album": {
                        "id": "12345",
                        "album_type": "album",
                        "release_date": "2020-02-02",
                        "release_date_precision": "day"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                },{
                    "name": "Some Song",
                    "album": {
                        "id": "2345",
                        "release_date": "2019-02",
                        "album_type": "album",
                        "release_date_precision": "month"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                },{
                    "name": "Some Song",
                    "album": {
                        "id": "3456",
                        "release_date": "2018",
                        "album_type": "album",
                        "release_date_precision": "year"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                },{
                    "name": "Some Song",
                    "album": {
                        "id": "4567",
                        "release_date": "hahaha",
                        "album_type": "album"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                }]
            }
        }
        """
        import json
        spotify_mock().search = Mock(name="search mock", return_value=json.loads(mock_response))
        api = SpotifyAPI()
        self.assertEqual(api.find_album_links([{"band": "Some Artist", "song": "Some Song"}]), ["3456"])

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_find_album_links_filters_non_albums(self, _, spotify_mock):
        mock_response= """{
            "tracks": {
                "items": [{
                    "name": "Some Song",
                    "album": {
                        "id": "12345",
                        "album_type": "single",
                        "release_date": "2018-01-01",
                        "release_date_precision": "day"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                },{
                    "name": "Some Song",
                    "album": {
                        "id": "2345",
                        "release_date": "2019-01-01",
                        "album_type": "album",
                        "release_date_precision": "day"
                    },
                    "artists": [{
                        "name": "Some Artist"
                    }]
                }]
            }
        }
        """
        import json
        spotify_mock().search = Mock(name="search mock", return_value=json.loads(mock_response))
        api = SpotifyAPI()
        self.assertEqual(api.find_album_links([{"band": "Some Artist", "song": "Some Song"}]), ["2345"])

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_create_playlists_adds_album_tracks_to_new_playlists(self, auth_mock, spotify_mock):
        spotify_mock().user_playlist_create = Mock(return_value={"id": "12345"})
        spotify_mock().album_tracks = Mock(return_value={"items": [{"id": "track1"}, {"id": "track2"}]})
        api = SpotifyAPI()
        api.user = "abc123"
        api.create_playlist("some_playlist", ["spotify:album:12345"])
        spotify_mock().user_playlist_add_tracks.assert_any_call("abc123", "12345", ["track1", "track2"])

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_create_playlists_adds_new_tracks_to_existing_playlists(self, auth_mock, spotify_mock):
        spotify_mock().user_playlists = Mock(return_value={"items": [{"id": "12345","name": "playlist1234"}]})
        spotify_mock().album_tracks = Mock(return_value={"items": [{"id": "track1"}, {"id": "track2"}]})
        spotify_mock().user_playlist_tracks = Mock(return_value={"items": [{"track": {"id": "track1"}}]})
        api = SpotifyAPI()
        api.user = "abc123"
        api.create_playlist("playlist1234", ["spotify:album:12345"])
        spotify_mock().user_playlist_add_tracks.assert_any_call("abc123", "12345", ["track2"])

    @patch("spotipy.Spotify")
    @patch("spotipy.util.prompt_for_user_token", return_value=True)
    def test_create_playlists_errors_when_multiple_playlists_match(self, auth_mock, spotify_mock):
        spotify_mock().user_playlists = Mock(return_value={"items": [{"id": "23456","name": "playlist1234"}, {"id": "12345","name": "playlist1234"}]})
        api = SpotifyAPI()
        api.user = "abc123"
        self.assertRaises(RuntimeError, api.create_playlist, "playlist1234", ["spotify:album:12345"])
