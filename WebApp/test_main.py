from unittest import TestCase
from test.support import EnvironmentVarGuard
with EnvironmentVarGuard() as env:
    env['SQLALCHEMY_DATABASE_URI'] = 'SQLALCHEMY_DATABASE_URI'
    import main


    class Test_main(TestCase):

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
