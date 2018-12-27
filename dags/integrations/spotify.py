import spotipy
import spotipy.util as util

class SpotifyAPI:
    def __init__(self):
        scope = 'playlist-modify-private user-follow-read'

        token = util.prompt_for_user_token('1237967510', scope, client_id='80dbe1a0f3144ee39a55e4faaa5e1aea', client_secret='0e14e6cc3e7f4c05ac8cc49cde3a5df3', redirect_uri="http://localhost:3333")

        if token:
            self.token = token
        else:
            raise RuntimeError("Couldn't authorize")
