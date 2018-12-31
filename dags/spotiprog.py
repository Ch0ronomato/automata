from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from integrations.reddit import CurrentDaysBands
from integrations.spotify import SpotifyAPI

def get_reddit_posts(reddit, **context):
    return reddit.get_bands(context['yesterday_ds'])

def get_spotify_albums(spotify, **context):
    return spotify.find_album_links(context['task_instance'].xcom_pull(task_ids='fetch_reddit_posts'))

def make_spotify_playlist(spotify, **context):
    spotify.create_playlist(
        "r/progmetal-" + context['yesterday_ds'], 
        context['task_instance'].xcom_pull(task_ids='fetch_spotify_albums')
    )

default_args = {
    'owner': 'chr0nomaton',
    'depends_on_past': False,
    'email': ['schweerian33@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('Automata', start_date=datetime(2018, 12, 30), default_args=default_args, schedule_interval=timedelta(days=1))

reddit = CurrentDaysBands()
spotify = SpotifyAPI()

t1_get_bands = PythonOperator(
    task_id='fetch_reddit_posts',
    python_callable=get_reddit_posts,
    op_args=[reddit],
    provide_context=True,
    dag=dag
)

t2_get_albums = PythonOperator(
    task_id='fetch_spotify_albums',
    python_callable=get_spotify_albums,
    op_args=[spotify],
    provide_context=True
)

t3_create_playlists = PythonOperator(
    task_id='create_playlists',
    python_callable=make_spotify_playlist,
    op_args=[spotify],
    provide_context=True
)

t1_get_bands >> t2_get_albums >> t3_create_playlists
