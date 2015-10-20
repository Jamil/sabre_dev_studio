import unittest
import json
import sys

sys.path.append('..')
import sabre_dev_studio.air.instaflights as instaflights

'''
tests for the sabredevstudio base class
requires config.json in the same directory for api authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBasicInstaflights(unittest.TestCase):
    def read_config(self):
        raw_data = open('config.json').read()

        data = json.loads(raw_data)

        client_secret = data['sabre_client_secret']
        client_id = data['sabre_client_id']

        return (client_id, client_secret)

    def setUp(self):
        # read from config
        self.client_id, self.client_secret = self.read_config()

    def test_init(self):
        instaf = instaflights.Instaflights(self.client_id, self.client_secret)

if __name__ == '__main__':
    unittest.main()
