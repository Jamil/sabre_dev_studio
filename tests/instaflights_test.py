import unittest
import json
import sys

sys.path.append('..')
import sabre_dev_studio

'''
requires config.json in the same directory for api authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBasicInstaflights(unittest.TestCase):
    def prepare_client(self):
        raw_data = open('config.json').read()

        data = json.loads(raw_data)

        client_secret = data['sabre_client_secret']
        client_id = data['sabre_client_id']

        sds = SabreDevStudio()
        sds.set_credentials(client_id, client_secret)
        sds.authenticate()

    def setUp(self):
        self.prepare_client()

    def test_init(self):
        instaf = instaflights.Instaflights(self.client_id, self.client_secret)

if __name__ == '__main__':
    unittest.main()
