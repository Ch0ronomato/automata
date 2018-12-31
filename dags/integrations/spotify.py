import spotipy
import spotipy.util as util
from datetime import date, datetime

class SpotifyAPI:
    def __init__(self):
        scope = 'playlist-modify-public playlist-modify-private user-follow-read'
        self.user = '1237967510'
        token = util.prompt_for_user_token(self.user, scope, client_id='80dbe1a0f3144ee39a55e4faaa5e1aea', client_secret='0e14e6cc3e7f4c05ac8cc49cde3a5df3', redirect_uri="http://localhost:3333")

        if token:
            self.token = token
            self.sp = spotipy.Spotify(auth=token)
        else:
            raise RuntimeError("Couldn't authorize")

    
    def find_album_links(self, songs_by_bands):
        album_ids = []
        for song_by_band in songs_by_bands:
            query = "track:{song} artist:{band}".format(**song_by_band)
            results = self.sp.search(q=query)
            if len(results["tracks"]["items"]) == 0:
                continue
            album_ids.append(self._get_oldest_matched_album(results))
            print("Found album {album} for {band}, {song}".format(
                album=album_ids[-1], 
                band=song_by_band["band"],
                song=song_by_band["song"],
            ))
        return album_ids

    def _get_oldest_matched_album(self, results):
        date_format = '%Y-%m-%d'
        first_released_album = 0
        for i, track in enumerate(results["tracks"]["items"][1:]):
            oldest_track = results["tracks"]["items"][first_released_album]
            current_track_release_date = datetime.strptime(track["album"]["release_date"], date_format)
            oldest_track_release_date = datetime.strptime(oldest_track["album"]["release_date"], date_format)
            if current_track_release_date < oldest_track_release_date:
                first_released_album = i + 1
        return results["tracks"]["items"][first_released_album]["album"]["id"]


    def create_playlist(self, playlist_name, spotify_album_ids):
        all_tracks = [
            track
            for album_id
            in spotify_album_ids
            for track
            in self.sp.album_tracks(album_id).pop("items")
        ]
        matched_playlists = [
            playlist
            for playlist
            in self.sp.user_playlists(self.user).pop("items")
            if playlist["name"] == playlist_name
        ]
        if len(matched_playlists) > 1:
            raise RuntimeError("Too many playlists matched name {name}, {playlists}".format(
                name=playlist_name,
                playlists=",".join([x["name"] for x in matched_playlists])
            ))
        elif len(matched_playlists) == 1:
            playlist = matched_playlists.pop()
            playlist_tracks = {
                x["track"]["id"]
                for x
                in self.sp.user_playlist_tracks(self.user, playlist["id"]).pop("items")
            }
            all_tracks = filter(lambda track: track["id"] not in playlist_tracks, all_tracks)
        else:
            playlist = self.sp.user_playlist_create(self.user, playlist_name)
        self._add_tracks_to_playlist(playlist["id"], all_tracks)

    def _add_tracks_to_playlist(self, playlist_id, all_tracks):
        track_ids = [track["id"] for track in all_tracks]
        if not track_ids:
            print("No tracks are new, nothing to do")
            return
        self.sp.user_playlist_add_tracks(self.user, playlist_id, track_ids)
