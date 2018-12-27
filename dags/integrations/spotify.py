import spotipy
import spotipy.util as util
from datetime import date

class SpotifyAPI:
    def __init__(self):
        scope = 'playlist-modify-private user-follow-read'
        self.user = '1237967510'
        token = util.prompt_for_user_token(self.user, scope, client_id='80dbe1a0f3144ee39a55e4faaa5e1aea', client_secret='0e14e6cc3e7f4c05ac8cc49cde3a5df3', redirect_uri="http://localhost:3333")

        if token:
            self.token = token
            self.sp = spotipy.Spotify(auth=token)
        else:
            raise RuntimeError("Couldn't authorize")
        # user_playlist_create 
        # current_user_followed_artists 
        # user_playlist_add_tracks 

    
    def find_album_links(self, songs_by_bands):
        for song_by_band in songs_by_bands:
            query = "track:{song} artist:{band}".format(**song_by_band)
            results = self.sp.search(q=query)
            # for tracks in results["tracks"]["items"]:

    def create_playlist(self, spotify_album_ids, reddit_name="progmetal"):
        date_string = date.today().strftime('%Y-%m-%d')
        playlist = self.sp.user_playlist_create(self.user, f"r/{reddit_name}-{date_string}", public=False)
        for album_id in spotify_album_ids:
            tracks = self.sp.album_tracks(album_id)
            self.sp.user_playlist_add_tracks(self.user, playlist["id"], [track["id"] for track in tracks["items"]])
        with open("/opt/playlist.json", "w+") as f:
            import json
            f.write(json.dumps(playlist))
