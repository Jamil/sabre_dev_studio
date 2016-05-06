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
class TestAirUtilities(unittest.TestCase):
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

    def test_alliance_request(self):
        res = self.sds.alliance_lookup('*A')
        
        airline_data = res.alliance_info[0].airline_info
        airline_codes = map(lambda rd: rd.airline_code, airline_data)

        self.assertIsNotNone(res)

        # This test should pass as long as Air Canada is in Star Alliance
        # and the function works ;)
        self.assertTrue('AC' in airline_codes)

    def test_equipment_lookup(self):
        res = self.sds.equipment_lookup('CR9')

        self.assertEqual(res, 'CANADAIR REGIONAL')
        
    def test_multi_city_airport_lookup(self):
        res = self.sds.multi_city_airport_lookup('GB')
        codes = map(lambda c: c.code, res)

        self.assertTrue('LON' in codes)

    def test_multi_city_airport_lookup(self):
        res = self.sds.countries_lookup('GB')
        origin_names = map(lambda c: c.country_name, res.origin_countries)
        destination_names = map(lambda c: c.country_name, res.destination_countries)

        self.assertTrue('United Kingdom' in origin_names)
        self.assertTrue('United Kingdom' in destination_names)

    def test_city_pairs_lookup(self):
        # SHOP
        # Country -> Country
        res = self.sds.city_pairs_lookup('shop', origin_country='US',
                                         destination_country='CA')
        locations = res.origin_destination_locations
        pairs = map(lambda l: l.origin_destination_locations, locations)

        self.assertTrue('JFK-YYZ' in pairs)

        # HISTORICAL
        # Region -> Region
        res = self.sds.city_pairs_lookup('shop', origin_region='North America',
                                         destination_region='Latin America')
        locations = res.origin_destination_locations
        pairs = map(lambda l: l.origin_destination_locations, locations)

        self.assertTrue('ATL-CUN' in pairs)

        # FORECAST
        # Country -> Region
        res = self.sds.city_pairs_lookup('shop', origin_country='US',
                                         destination_region='Europe')
        locations = res.origin_destination_locations
        pairs = map(lambda l: l.origin_destination_locations, locations)

        self.assertTrue('SFO-LHR' in pairs)

if __name__ == '__main__':
    unittest.main()
