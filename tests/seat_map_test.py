import unittest
import datetime
import json
import sys

sys.path.append('..')
import sabre_dev_studio
import sabre_dev_studio.sabre_exceptions as sabre_exceptions
import sabre_dev_studio.sabre_utils as sabre_utils

'''
requires config.json in the same directory for api authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBasicSeatMap(unittest.TestCase):
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
        now = datetime.datetime.now()

        tomorrow = now + datetime.timedelta(days=1)

        smap = self.sds.seat_map('JFK', 'LAX', tomorrow, 'AA', 1)

        self.assertIsNotNone(smap)

    def test_basic_request(self):
        now = datetime.datetime.now()

        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')

        options = {
            "EnhancedSeatMapRQ": {
                "SeatMapQueryEnhanced": {
                    "RequestType": "Payload",
                    "Flight": {
                        "destination": "EZE",
                        "origin": "DFW",
                        "DepartureDate": {
                            "content": tomorrow_str
                        },
                        "Marketing": [{
                            "carrier": "AA",
                            "content": "997"
                        }]
                    }
                }
            }
        }

        smap = self.sds.seat_map_opts(options)

        self.assertIsNotNone(smap)
        

if __name__ == '__main__':
    unittest.main()
