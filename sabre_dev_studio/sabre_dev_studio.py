import requests
import json
import base64
import datetime
import collections
import re

# Local imports
import sabre_exceptions
import sabre_endpoints


class SabreDevStudio(object):
    def __init__(self):
        self.auth_headers = None

        self.client_id = None
        self.client_secret = None
        self.token = None
        self.token_expiry = None

        self.host = 'https://api.test.sabre.com'

    # make_endpoint
    # String -> String
    # Converts a relative endpoint to an absolute URI
    def make_endpoint(self, endpoint):
        return self.host + endpoint

    # set_credentials
    # String -> String -> ()
    # Sets the Sabre Dev Studio Client ID and Secret to the instance
    # Must be done before token is requested
    def set_credentials(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret 

    # authenticate
    # () -> ()
    # This method uses the client ID and client secret provided in set_credentials
    # to request the token from Sabre. The token is then saved in the internal state
    # of the instance in self.token
    def authenticate(self):
        if not self.client_id or not self.client_secret:
            raise sabre_exceptions.NoCredentialsProvided

        token_resp = self.get_token_data(self.client_id, self.client_secret)
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

        data = requests.post(self.make_endpoint('/v2/auth/token/'),
                             headers=headers,
                             data=payload)

        return data

    # request
    # String -> String -> Dictionary -> ResponseData
    # The generic request function -- all API requests go through here
    # Should be called by a higher-level wrapper like instaflights(...)
    #    method is a String, 'GET', 'PUT', 'PATCH', 'POST', or 'DELETE'
    #    endpoint is a relative endpoint
    #    payload is the data -- added as query params for GET
    # Returns an object with the properties of the response data
    def request(self, method, endpoint, payload=None):
        now = datetime.datetime.now()

        # Check for token
        if not self.token:
            raise sabre_exceptions.NotAuthorizedError

        if not self.token_expiry:
            pass
        elif self.token_expiry < now:
            # Authenticate again
            self.authenticate()

        endpoint = self.make_endpoint(endpoint)
        auth_header = {
            "Authorization": "Bearer" + self.token
        }

        if method == 'GET':
            resp = requests.get(endpoint, headers=auth_header)
        elif method == 'PUT':
            resp = requests.put(endpoint, headers=auth_header, data=payload)
        elif method == 'PATCH':
            resp = requests.put(endpoint, headers=auth_header, data=payload)
        elif method == 'POST':
            resp = requests.post(endpoint, headers=auth_header, data=payload)
        elif method == 'DELETE':
            resp = requests.delete(endpoint, headers=auth_header)
        else:
            raise UnsupportedMethodError

        self.verify_response(resp)
        resp_data = self.process_response(resp.json())
        return resp_data

    # verify_response
    # Response -> ()
    # Checks the status code of a response and raises the appropriate exception
    # if the status code is invalid (not in the 2xx range)
    def verify_response(self, resp):
        if resp.status_code >= 200 and resp.status_code < 299:
            pass

        elif resp.status_code == 400:
            raise sabre_exceptions.SabreErrorBadRequest
        elif resp.status_code == 401:
            raise sabre_exceptions.SabreErrorUnauthenticated
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
        
    # process_response
    # JSON Dictionary -> ResponseData
    # Converts a dictionary into a python object with Pythonic names
    def process_response(self, json_obj):
        def convert_keys(d):
            if isinstance(d, list):
                for elem in d:
                    convert_keys(elem)
                return
            elif not isinstance(d, dict):
                return

            for key in d.keys():
                s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
                s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
                s = re.sub('[^0-9a-zA-Z]+', '_', s)
                s = re.sub('^[0-9]', '', s)
                
                s = s.replace(' ', '_')
                d[s] = d[key]
                if s != key:
                    del d[key]

                convert_keys(d[s])
            
        convert_keys(json_obj)

        json_str = json.dumps(json_obj)
        obj = json.loads(json_str,
                         object_hook=lambda d: collections.namedtuple('ResponseData', d.keys())(*d.values()))
            
        return obj

    # instaflights
    # Dictionary -> ResponseData
    # Executes a request to Sabre's instaflights endpoint with the options specified
    def instaflights(self, options):
        pass
        
