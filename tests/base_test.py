import unittest
import json
import sys
import datetime

sys.path.append('..')

import sabre_dev_studio
import sabre_dev_studio.sabre_exceptions as sabre_exceptions

'''
Tests for the SabreDevStudio base class
Requires config.json in the same directory for API authentication

{
	"sabre_client_id": -----,
	"sabre_client_secret": -----
}

'''
class TestBasicSabreDevStudio(unittest.TestCase):
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
        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(self.client_id, self.client_secret)
        sds.authenticate()

    def test_basic_get(self):
        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(self.client_id, self.client_secret)
        sds.authenticate()
        
        # We're not going to check the contents of the response here
        # Just that it returned 200 OK
        resp = sds.request('GET', '/v1/lists/supported/cities/YTO/airports/')

    def test_token_set(self):
        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(self.client_id, self.client_secret)
        sds.authenticate()

        token = sds.token
        sds2 = sabre_dev_studio.SabreDevStudio()
        sds2.token = token
        sds2.token_expiry = datetime.datetime.now() + datetime.timedelta(0, 60)

        # Test endpoint
        resp = sds2.request('GET', '/v1/lists/supported/cities/YTO/airports/')

    def test_expired_token(self):
        sds = sabre_dev_studio.SabreDevStudio()
        sds.token = '000'
        sds.token_expiry = datetime.datetime.now()

        with self.assertRaises(sabre_exceptions.NoCredentialsProvided):
            resp = sds.request('GET', '/v1/lists/supported/cities/YTO/airports/')

    def test_no_authorization(self):
        sds = sabre_dev_studio.SabreDevStudio()

        with self.assertRaises(sabre_exceptions.NotAuthorizedError):
            resp = sds.request('GET', '/v1/lists/supported/cities/YTO/airports/')

    def test_invalid_location(self):
        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(self.client_id, self.client_secret)
        sds.authenticate()
        
        with self.assertRaises(sabre_exceptions.SabreErrorNotFound):
            resp = sds.request('GET', '/v1/lists/supported/cities/Toronto/airports/')

    def test_get_json(self):
        sds = sabre_dev_studio.SabreDevStudio()
        sds.set_credentials(self.client_id, self.client_secret)
        sds.authenticate()

        resp = sds.request('GET', '/v1/lists/supported/cities/YTO/airports/')
        self.assertTrue(isinstance(resp, dict))
        
    def test_process_response(self):
        raw_data = open('sample_json.json').read()
        self.assertIsNotNone(raw_data)

        data = json.loads(raw_data)
        self.assertIsNotNone(data)

        sds = sabre_dev_studio.SabreDevStudio()
        resp = sds.process_response(data)

        self.assertTrue(hasattr(resp, 'colors_array'))
        self.assertFalse(hasattr(resp, 'colorsArray'))

        self.assertEqual(len(resp.colors_array), 7)

        self.assertTrue(hasattr(resp.colors_array[1], 'color_name'))
        self.assertFalse(hasattr(resp.colors_array[1], 'colorName'))
        self.assertEqual(resp.colors_array[0].color_name, 'red')

    def test_convert_key_special_chars(self):
        sds = sabre_dev_studio.SabreDevStudio()

        # Whitespace in key
        data = json.loads('{"whitespace test": "empty"}')
        resp = sds.process_response(data)
        self.assertTrue(hasattr(resp, 'whitespace_test'))

        # Non-alphanumeric characters
        # Check that it doesn't fail
        data = json.loads('{"special% char\' test!": "empty"}')
        resp = sds.process_response(data)
        self.assertTrue(hasattr(resp, 'special_char_test'))

        # Key starting with a number
        data = json.loads('{"1number_start_test": "empty"}')
        resp = sds.process_response(data)
        self.assertTrue(hasattr(resp, 'number_start_test'))

        # Key ending with a number
        data = json.loads('{"NumberEndTest1": "empty"}')
        resp = sds.process_response(data)
        self.assertTrue(hasattr(resp, 'number_end_test1'))

        # Key with multiple contiguous special characters
        data = json.loads('{"multiple__Contiguous!!!SpecialCharacters%%%%": "empty"}')
        resp = sds.process_response(data)
        self.assertTrue(hasattr(resp, 'multiple_contiguous_special_characters'))

    def test_convert_date(self):
        now = datetime.datetime.now()
        string_representation = now.stftime('%Y-%m-%d')

        sds = sabre_dev_studio.SabreDevStudio()
        self.assertEqual(sds.convert_date(now), string_representation)

if __name__ == '__main__':
    unittest.main()
