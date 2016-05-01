import unittest
import datetime
import json
import sys

sys.path.append('..')
import sabre_dev_studio
import sabre_dev_studio.sabre_exceptions as sabre_exceptions

'''
requires config.json in the same directory for api authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBasicTopDestinations(unittest.TestCase):
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

    def test_fn_request(self):
        res = self.sds.top_destinations('YYZ', theme='beach',
                                        destination_type='INTERNATIONAL',
                                        region='North America')
        self.assertIsNotNone(res)

    def test_basic_request(self):
        options = {
            'origin': 'YYZ',
            'destinationtype': 'DOMESTIC',
            'lookbackweeks': 2,
            'topdestinations': 20
        }
        res = self.sds.top_destinations_opts(options)
        self.assertIsNotNone(res)

    def test_no_authorization(self):
        sds = sabre_dev_studio.SabreDevStudio()

        with self.assertRaises(sabre_exceptions.NotAuthorizedError):
            resp = sds.instaflights({})


if __name__ == '__main__':
    unittest.main()
