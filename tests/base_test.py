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

        


if __name__ == '__main__':
    unittest.main()
