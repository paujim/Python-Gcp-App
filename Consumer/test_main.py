from unittest import TestCase
import main


class TestMain(TestCase):

    def test_get_attribute(self):
        main.app.testing = True

        response_obj = {
            'message': {
                'attributes': {
                    'validkey': 'testValue'
                }
            }
        }
        text = main.get_attribute(response_obj, "notValid")
        self.assertIsNone(text)
        text = main.get_attribute(response_obj, "validkey")
        self.assertEqual("testValue", text)


