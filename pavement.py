import os
import sys
sys.path.append(os.path.dirname(__file__))
from paver.easy import sh, task, needs, consume_args
from profilehooks import timecall

@task
@timecall
def test_dags():
    """Execute Python test suite and generate a code coverage report
    """
    sh('python -m pytest --junitxml=/tmp/tests.xml --cov=dags --cov=util --cov-report xml:/tmp/coverage.xml --cov-report term-missing:skip-covered -v test/')

@task
@consume_args
def airflow(args):
    command = 'webserver'
    if args:
        command = args.pop()
    sh(f'/entrypoint.sh {command}')

@task
@consume_args
def makes_a_playlist(args):
    if not args:
        raise RuntimeError("Give me a date")
    date = args[0]
    from dags.integrations.reddit import CurrentDaysBands
    from dags.integrations.spotify import SpotifyAPI
    spotify = SpotifyAPI()
    reddit = CurrentDaysBands()
    songs_posted = reddit.get_bands(date)
    print("Found songs {}".format(songs_posted))
    spotify_albums = spotify.find_album_links(songs_posted)
    print("Found albums {}".format(spotify_albums))
    spotify.create_playlist("r/progmetal-" + date, spotify_albums)
    print("Check spotify?")
