from unittest import TestCase
import main
import datetime


class Test_main(TestCase):


    def test_index(self):
        main.app.testing = True
        client = main.app.test_client()
        r = client.get('/')
        self.assertEqual(r.status_code, 200)

    def test_classify_sentiment(self):
        main.app.testing = True
        text = main.classify_sentiment(None)
        self.assertEqual("Not Available", text)

        text = main.classify_sentiment([(0.9, 0.5, None, "text")])
        self.assertEqual("Clearly Positive", text)

        text = main.classify_sentiment([(0.2, 0.5, None, "text")])
        self.assertEqual("Positive", text)

        text = main.classify_sentiment([(-0.9, 0.5, None, "text")])
        self.assertEqual("Clearly Negative", text)

        text = main.classify_sentiment([(-0.2, 0.5, None, "text")])
        self.assertEqual("Negative", text)

        text = main.classify_sentiment([(0.09, 0.5, None, "text")])
        self.assertEqual("Neutral", text)

        text = main.classify_sentiment([(-0.09, 0.5, None, "text")])
        self.assertEqual("Neutral", text)
