import requests
import json
import base64
import datetime

# Local imports
import sabre_exceptions

class SabreDevStudio(object):
    def __init__(self, client_id, client_secret):
        self.id = client_id
        self.secret = client_secret

    def authorize(self):
        token_resp = self.get_token_data(self.id, self.secret)
        self.verify_response(token_resp)

        token_json = token_resp.json()
        
        self.token = token_json.get('access_token')
        self.token_expiry = datetime.datetime.now() + datetime.timedelta(0, token_json.get('expires_in'))

    def get_token_data(self, client_id, client_secret):
        encoded = str(base64.b64encode(client_id)) + ':' + str(base64.b64encode(client_secret))

        encoded = str(base64.b64encode(encoded))

        headers = {
            'Authorization': 'Basic ' + encoded,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {
            'grant_type': 'client_credentials'
        }

        data = requests.post('https://api.test.sabre.com/v2/auth/token',
                             headers=headers,
                             data=payload)

        return data

    def verify_response(self, resp):
        if resp.status_code == 200:
            pass

        elif resp.status_code == 400:
            raise sabre_exceptions.SabreErrorBadRequest
        elif resp.status_code == 401:
            raise sabre_exceptions.SabreErrorUnauthorized
        elif resp.status_code == 403:
            raise sabre_exceptions.SabreErrorForbidden
        elif resp.status_code == 404:
            raise sabre_exceptions.SabreErrorNotFound
        elif resp.status_code == 406:
            raise sabre_exceptions.SabreErrorNotAcceptable
        elif resp.status_code == 429:
            raise sabre_exceptions.SabreErrorRateLimited

        elif resp.status_code == 500:
            raise sabre_exceptions.SabreInternalServerError
        elif resp.status_code == 503:
            raise sabre_exceptions.SabreErrorServiceUnavailable
        elif resp.status_code == 503:
            raise sabre_exceptions.SabreErrorGatewayTimeout
        
