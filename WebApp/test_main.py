
from unittest import TestCase, mock
from test.support import EnvironmentVarGuard

with EnvironmentVarGuard() as env:
    env['SQLALCHEMY_DATABASE_URI'] = 'SQLALCHEMY_DATABASE_URI'
    import main
    from main import Tweet

    class TestMain(TestCase):

        def test_classify_sentiment(self):
            main.app.testing = True
            text = main.classify_sentiment(None)
            self.assertEqual("Not Available", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=0.9, magnitude=0.5)])
            self.assertEqual("Clearly Positive", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=0.2, magnitude=0.5)])
            self.assertEqual("Positive", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=-0.9, magnitude=0.5)])
            self.assertEqual("Clearly Negative", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=-0.2, magnitude=0.5)])
            self.assertEqual("Negative", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=0.09, magnitude=0.5)])
            self.assertEqual("Neutral", text)

            text = main.classify_sentiment([dict(text="text", timestanp=None, score=-0.09, magnitude=0.5)])
            self.assertEqual("Neutral", text)

        @mock.patch("main.Tweet")
        def test_fetch_data_with_expected_format(self, model_mock):

            # set up
            model_mock.query.\
                group_by(Tweet.timestamp, Tweet.text).\
                order_by(Tweet.timestamp.desc()).\
                limit(5).\
                all.return_value = [
                    Tweet("tweet text", "keyword", None, "location", 0.1, 1.0),
                    Tweet("text two",  "keyword two", None, "location two", 0.2, 2.0)]

            data = main.fetch_data()
            self.assertEqual(2, len(data))
            self.assertEqual('tweet text', data[0]['text'])
            self.assertEqual('keyword', data[0]['keyword'])
            self.assertIsNone(data[0]['timestamp'])
            self.assertEqual(0.1, data[0]['score'])
            self.assertEqual(1.0, data[0]['magnitude'])
