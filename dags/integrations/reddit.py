import praw
from datetime import datetime, timedelta
class CurrentDaysBands:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id='nApgfjw6px0iJA',
            client_secret='yd4dO03N9oJwjXz3SzpOtQZzJYM',
            user_agent='aws:spotiprog:v0.0.1 (by /u/Chr0nomaton)',
        )

    def get_sub(self):
        return self.reddit.subreddit('progmetal')

    def get_bands(self, day_to_grab):
        posts = self.get_sub().new(limit=500)
        return [
            {
                "band": post.title.split("-")[0].strip(),
                "album": post.title.split("-")[1].strip(),
            }
            for post
            in posts
            if datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d') == day_to_grab
            and 'youtube.com' in post.url
        ]

