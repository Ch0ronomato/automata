import unittest
from dags.integrations.reddit import CurrentDaysBands
from unittest.mock import Mock, call, patch, PropertyMock
from collections import namedtuple
from datetime import datetime, timedelta

def get_utc_timestamp(timespan):
    now = datetime.utcnow()
    epoch = datetime(1970,1,1)
    return (now - timespan - epoch).total_seconds()

class TestReddit(unittest.TestCase):
    def setUp(self):
        self.unit = CurrentDaysBands()

    @patch("dags.integrations.reddit.CurrentDaysBands.get_sub")
    def test_reddit_skips_after_date(self, get_sub_mock):
        Listing = namedtuple("Listing", ["title", "url", "created_utc"])
        listings_fetching_mock = (
            x 
            for x 
            in [
                Listing(title="Some Artist - Some Album", url="www.youtube.com", created_utc=get_utc_timestamp(timedelta(days=1))),
                Listing(title="Another Artist - Some Album", url="www.youtube.com", created_utc=get_utc_timestamp(timedelta(days=10))),
                Listing(title="Yet Another Artist - Some Album", url="www.youtube.com", created_utc=get_utc_timestamp(timedelta(days=20))),
            ]
        )
        new_posts_mock = Mock(name="mymock")
        new_posts_mock.new.return_value = listings_fetching_mock
        get_sub_mock.return_value = new_posts_mock
        date_to_grab = (datetime.utcnow() - timedelta(days=10)).strftime('%Y-%m-%d')
        self.assertEqual(self.unit.get_bands(date_to_grab), [{"band": "Another Artist", "album": "Some Album"}])
