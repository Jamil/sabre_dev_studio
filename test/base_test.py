import unittest
import json

from sabre_dev_studio import SabreDevStudio

'''
Tests for the SabreDevStudio base class
Requires config.json in the same directory for API authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBaseSabreDevStudio(unittest.TestCase):
    def read_config(self):
        raw_data = open('config.json').read()

        data = json.loads(raw_data)

        client_secret = data['sabre_client_secret']
        client_id = data['sabre_client_id']

        return (client_id, client_secret)

    def setUp(self):
        # Read from config
        self.client_id, self.client_secret = self.read_config()

    def test_auth(self):
        sds = SabreDevStudio(self.client_id, self.client_secret)
        sds.authorize()

if __name__ == '__main__':
    unittest.main()
