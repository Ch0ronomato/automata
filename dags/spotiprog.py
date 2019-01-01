from airflow import DAG
from airflow.models import Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from integrations.reddit import CurrentDaysBands
from integrations.spotify import SpotifyAPI

def get_reddit_posts(**context):
    reddit = CurrentDaysBands(
       client_id=Variable.get("REDDIT_CLIENT_ID"),
       client_secret=Variable.get("REDDIT_CLIENT_SECRET"),
       user_agent=Variable.get("REDDIT_USER_AGENT")
    )
    return reddit.get_bands(context['yesterday_ds'])

def get_spotify_albums(spotify, **context):
    return spotify.find_album_links(context['task_instance'].xcom_pull(task_ids='fetch_reddit_posts'))

def make_spotify_playlist(spotify, **context):
    yesterday = datetime.strptime(context['yesterday_ds'], '%Y-%m-%d')
    playlist_date = yesterday - timedelta(days=yesterday.weekday())
    spotify.create_playlist(
        "r/progmetal-" + playlist_date.strftime("%Y-%m-%d"),
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

user_id = Variable.get("SPOTIFY_CLIENT_USER_ID")
auth_token = Variable.get("SPOTIFY_CLIENT_TOKEN_CACHE")
with open(f"/usr/local/airflow/.cache-{user_id}", "w+") as f:
    print(f"Wrote {auth_token} to /usr/local/airflow/.cache-{user_id}")
    f.write(auth_token)
spotify = SpotifyAPI(
    user_id=user_id,
    client_id=Variable.get("SPOTIFY_CLIENT_ID"),
    client_secret=Variable.get("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=Variable.get("SPOTIFY_CLIENT_REDIRECT_URI"),
)
with open(f"/usr/local/airflow/.cache-{user_id}") as f:
    Variable.set("SPOTIFY_CLIENT_TOKEN_CACHE", f.read())

t1_get_bands = PythonOperator(
    task_id='fetch_reddit_posts',
    python_callable=get_reddit_posts,
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
