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
class TestBasicLeadPrice(unittest.TestCase):
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

    def test_request_with_args(self):
        prices = self.sds.lead_price('YTO', 'SFO', [3,4], point_of_sale='CA')

        self.assertIsNotNone(prices)

    def test_basic_request(self):
        opts = {
            'origin': 'YTO',
            'destination': 'SFO',
            'lengthofstay': [3,4],
            'pointofsalecountry': 'CA'
        }

        prices = self.sds.lead_price_opts(opts)

        self.assertIsNotNone(prices)
        

if __name__ == '__main__':
    unittest.main()
