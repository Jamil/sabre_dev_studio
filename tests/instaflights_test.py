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
    def read_config(self):
        raw_data = open('config.json').read()

        data = json.loads(raw_data)

        client_secret = data['sabre_client_secret']
        client_id = data['sabre_client_id']

        return (client_id, client_secret)

    def setUp(self):
        # Read from config
        self.client_id, self.client_secret = self.read_config()
        self.sds = sabre_dev_studio.SabreDevStudio()
        self.sds.set_credentials(self.client_id, self.client_secret)
        self.sds.authenticate()

    def test_basic_request():
        now = datetime.datetime.now()

        tomorrow = now + timedelta(days=1)
        day_after = now + timedelta(days=2)
        
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

    def test_no_authorization(self):
        sds = sabre_dev_studio.SabreDevStudio()

        with self.assertRaises(sabre_exceptions.NotAuthorizedError):
            resp = sds.instaflights({})


if __name__ == '__main__':
    unittest.main()
