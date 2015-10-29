import unittest
import datetime
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

        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(client_id, client_secret)
        sds.authenticate()

        self.sds = sds

    def setUp(self):
        self.prepare_client()

    def test_basic_request(self):
        now = datetime.datetime.now()

        # Set departure date to tomorrow
        # Set arrival date to day after
        tomorrow = now + datetime.timedelta(days=1)
        day_after = now + datetime.timedelta(days=2)

        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        day_after_str = day_after.strftime('%Y-%m-%d')

        options = {
            'origin': 'JFK',
            'destination': 'LAX',
            'departuredate': tomorrow_str,
            'returndate': day_after_str
        }

        instaf = self.sds.instaflights(options)
        self.assertIsNotNone(instaf)

if __name__ == '__main__':
    unittest.main()
