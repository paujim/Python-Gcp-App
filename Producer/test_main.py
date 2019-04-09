from datetime import datetime
from unittest import TestCase, mock
from test.support import EnvironmentVarGuard

with EnvironmentVarGuard() as env:
    env['GOOGLE_CLOUD_PROJECT'] = 'NOT_SET'

    import main


    class TestMain(TestCase):

        def test_removing_user_and_link_from_tweets(self):
            main.app.testing = True
            clean_text = main.clean_tweets("RT @Freedom4Horses: Coyotes are canines and so closely related to dogs, they can breed with them. https://en.wikipedia.org")
            self.assertEquals("rt coyotes are canines and so closely related to dogs , they can breed with them .", clean_text)

        @mock.patch("main.search_tweets")
        def test_fetch_data_with_expected_format(self, model_mock):
            # Set up
            class MockUserObject(object):
                pass
            mock_user = MockUserObject()
            mock_user.location = 'some location'

            class MockTweetObject(object):
                pass
            mock_tweet = MockTweetObject()
            mock_tweet.text = 'some tweet text'
            mock_tweet.created_at = datetime(2000, 10, 10)
            mock_tweet.user = mock_user
            model_mock.return_value = [mock_tweet]

            data = main.fetch_tweets('key', 1)
            self.assertEqual(1, len(data))
            self.assertEqual('some tweet text', data[0]['tweet'])
            self.assertEqual('2000-10-10T00:00:00', data[0]['timestamp'])
            self.assertEqual('some location', data[0]['location'])
