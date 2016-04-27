import requests
import json
import base64
import datetime
import collections
import re

# Local imports
import sabre_utils
import sabre_exceptions
from sabre_endpoints import sabre_endpoints


class SabreDevStudio(object):
    def __init__(self, environment='test', return_obj=True):
        self.auth_headers = None

        self.client_id = None
        self.client_secret = None
        self.token = None
        self.token_expiry = None

        self.return_obj = return_obj

        if environment is 'test':
            self.host = 'https://api.test.sabre.com'
        elif environment is 'prod':
            self.host = 'https://api.sabre.com'
        else: # default to test
            self.host = 'https://api.test.sabre.com'

    # init_with_config
    # () -> ()
    # Initializes the class with an ID and secret from a config file
    # Useful for testing and interactive mode
    def init_with_config(self, config_file='config.json'):
        raw_data = open(config_file).read()

        data = json.loads(raw_data)

        client_secret = data['sabre_client_secret']
        client_id = data['sabre_client_id']

        self.set_credentials(client_id, client_secret)
        self.authenticate()

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
    # String -> String -> Dictionary -> (ResponseData or dict)
    # The generic request function -- all API requests go through here
    # Should be called by a higher-level wrapper like instaflights(...)
    #    method is a String, 'GET', 'PUT', 'PATCH', 'POST', or 'DELETE'
    #    endpoint is a relative endpoint
    #    payload is the data -- added as query params for GET
    # Returns an object with the properties of the response data
    def request(self, method, endpoint, payload=None, additional_headers=None):
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
            'Authorization': 'Bearer' + self.token
        }

        headers = additional_headers.copy() if additional_headers else {}
        headers.update(auth_header)

        if method == 'GET':
            resp = requests.get(endpoint, headers=headers, params=payload)
        elif method == 'PUT':
            resp = requests.put(endpoint, headers=headers, data=payload)
        elif method == 'PATCH':
            resp = requests.put(endpoint, headers=headers, data=payload)
        elif method == 'POST':
            resp = requests.post(endpoint, headers=headers, data=payload)
        elif method == 'DELETE':
            resp = requests.delete(endpoint, headers=headers)
        else:
            raise UnsupportedMethodError

        self.verify_response(resp)

        if self.return_obj:
            resp_data = self.process_response(resp.json())
        else:
            resp_data = resp.json()

        return resp_data

    # verify_response
    # Response -> ()
    # Checks the status code of a response and raises the appropriate exception
    # if the status code is invalid (not in the 2xx range)
    def verify_response(self, resp):
        if resp.status_code >= 200 and resp.status_code < 299:
            pass

        else:
            if resp.status_code == 400:
                raise sabre_exceptions.SabreErrorBadRequest(resp.json())
            elif resp.status_code == 401:
                raise sabre_exceptions.SabreErrorUnauthenticated(resp.json())
            elif resp.status_code == 403:
                raise sabre_exceptions.SabreErrorForbidden(resp.json())
            elif resp.status_code == 404:
                raise sabre_exceptions.SabreErrorNotFound(resp.json())
            elif resp.status_code == 405:
                raise sabre_exceptions.SabreErrorMethodNotAllowed()
            elif resp.status_code == 406:
                raise sabre_exceptions.SabreErrorNotAcceptable(resp.json())
            elif resp.status_code == 429:
                raise sabre_exceptions.SabreErrorRateLimited(resp.json())

            elif resp.status_code == 500:
                print(resp.text)
                raise sabre_exceptions.SabreInternalServerError(resp.text)
            elif resp.status_code == 503:
                raise sabre_exceptions.SabreErrorServiceUnavailable
            elif resp.status_code == 504:
                raise sabre_exceptions.SabreErrorGatewayTimeout

    # process_response
    # JSON Dictionary -> ResponseData
    # Converts a dictionary into a python object with Pythonic names
    def process_response(self, json_obj):
        sabre_utils.convert_keys(json_obj)

        json_str = json.dumps(json_obj)
        obj = json.loads(json_str,
                         object_hook=lambda d: collections.namedtuple('ResponseData', d.keys())(*d.values()))

        return obj

    # instaflights
    # Dictionary -> ResponseData
    # Executes a request to Sabre's instaflights endpoint with the options specified
    def instaflights(self, options):
        resp = self.request('GET', sabre_endpoints['instaflights'], options)
        return resp

    # flights_to
    # String -> String? -> ResponseData
    # Executes a request to Sabre's "Flights To" endpoint with the options specified
    # Returns 20 of the lowest published fares available for a given destination
    # Defaults to 'US' as point of sale
    def flights_to(self, city_code, point_of_sale=None):
        opts = {
            'pointofsalecountry': point_of_sale
        }

        resp = self.request('GET',
                            sabre_endpoints['flights_to'] + '/' + city_code,
                            opts)

        return resp

    # lead_price
    # String -> String -> [Number] -> ResponseData 
    # Executes a request to Sabre's "Lead Price" endpoint with the arguments specified
    # Gives the cheapest dates and fare for the specified origin, destination
    # and length of stay
    def lead_price(self, origin, destination, length_of_stay,
                   point_of_sale=None, departure_date=None, min_fare=None, 
                   max_fare=None, other_opts={}):

        opts = other_opts.copy()
        opts['origin'] = origin
        opts['destination'] = destination
        
        if point_of_sale:
            opts['pointofsalecountry'] = point_of_sale
        else:
            # Get point of sale country for origin
            result = country_code_lookup(origin)
            opts['pointofsalecountry'] = result if result else 'US'

        if length_of_stay is not None and isinstance(length_of_stay, list):
            opts['lengthofstay'] = ','.join(map(str, length_of_stay))
        elif length_of_stay is not None:
            opts['lengthofstay'] = length_of_stay

        if departure_date:
            opts['departuredate'] = self.convert_date(departure_date);
        if min_fare:
            opts['minfare'] = min_fare
        if max_fare:
            opts['maxfare'] = max_fare

        resp = self.request('GET',
                            sabre_endpoints['lead_price'],
                            opts)
        
        return resp

    # lead_price_opts
    # Dictionary -> ResponseData 
    # Executes a request to Sabre's "Lead Price" endpoint with the arguments specified
    # Gives the cheapest dates and fare for the specified origin, destination
    # and length of stay
    def lead_price_opts(self, opts):
        resp = self.request('GET',
                            sabre_endpoints['lead_price'],
                            opts)
        
        return resp


    # destination_finder
    # String -> String -> [Number] -> ResponseData 
    # Executes a request to Sabre's "Lead Price" endpoint with the arguments specified
    # Gives the cheapest dates and fare for the specified origin, destination
    # and length of stay
    def destination_finder(self, origin, destination=None, length_of_stay=None,
                           point_of_sale=None,
                           departure_date=None, return_date=None,
                           earliest_departure_date=None, latest_departure_date=None,
                           min_fare=None, max_fare=None,
                           region=None, theme=None, location=None,
                           cost_per_mile=None,
                           other_opts={}):

        opts = other_opts.copy()
        opts['origin'] = origin

        if point_of_sale:
            opts['pointofsalecountry'] = point_of_sale
        else:
            # Get point of sale country for origin
            result = country_code_lookup(origin)
            opts['pointofsalecountry'] = result if result else 'US'

        if destination:
            opts['destination'] = destination

        if length_of_stay is not None and isinstance(length_of_stay, list):
            opts['lengthofstay'] = ','.join(map(str, length_of_stay))
        elif length_of_stay is not None:
            opts['lengthofstay'] = length_of_stay

        if departure_date:
            opts['departuredate'] = self.convert_date(departure_date);
        if return_date:
            opts['returndate'] = self.convert_date(return_date);
        if earliest_departure_date:
            opts['earliestdeparturedate'] = self.convert_date(earliest_departure_date);
        if latest_departure_date:
            opts['latestdeparturedate'] = self.convert_date(latest_departure_date);
        if min_fare:
            opts['minfare'] = min_fare
        if max_fare:
            opts['maxfare'] = max_fare
        if region:
            opts['region'] = region
        if theme:
            opts['theme'] = theme
        if location:
            opts['location'] = location
        if cost_per_mile:
            opts['pricepermile'] = cost_per_mile

        resp = self.request('GET',
                            sabre_endpoints['destination_finder'],
                            opts)
        
        return resp


    # destination_finder_opts
    # Dictionary -> ResponseData 
    # Executes a request to Sabre's "Lead Price" endpoint with the options specified
    # as query parameters
    def destination_finder_opts(self, opts):
        resp = self.request('GET',
                            sabre_endpoints['destination_finder'],
                            opts)
        
        return resp

    # top_destinations
    # Dictionary -> ResponseData 
    # Executes a request to Sabre's "Top Destinations" endpoint with the 
    # options specified. Returns most popular destinations based on the params.
    # origin is 2 characters => interpreted as country
    # origin is 3 characters => interpreted as city
    # destinationtype = ['DOMESTIC', 'INTERNATIONAL', 'OVERALL']
    # weeks is the number of weeks to look back for data
    def top_destinations(self, origin, destination_type=None,
                         theme=None, num_results=20, destination_country=None,
                         region=None, weeks=2):

        opts = {}
        if len(origin) == 2:
            opts['origincountry'] = origin
        else:
            opts['origin'] = origin

        if destination_type:
            opts['destinationtype'] = destination_type
        if theme:
            opts['theme'] = theme
        if num_results:
            opts['topdestinations'] = num_results
        if destination_country:
            opts['destinationcountry'] = destination_country
        if region:
            opts['region'] = region
        if weeks:
            opts['lookbackweeks'] = weeks

        resp = self.request('GET',
                            sabre_endpoints['top_destinations'],
                            opts)
        return resp

    # top_destinations_opts
    # Dictionary -> ResponseData 
    # Executes a request to Sabre's "Top Destinations" endpoint with the 
    # options specified as query parameters. 
    def top_destinations_opts(self, opts):
        resp = self.request('GET',
                            sabre_endpoints['top_destinations'],
                            opts)
        
        return resp

    # country_code_lookup
    # String -> String?
    # Finds a country code given an airport/city code
    def country_code_lookup(self, code):
        opts = [{
            "GeoCodeRQ": {
                "PlaceById": {
                    "Id": code,
                    "BrowseCategory": {
                        "name": "AIR"
                    }
                }
            }
        }]

        try:
            resp = self.request('POST',
                                sabre_endpoints['geo_code'],
                                json.dumps(opts, sort_keys=True),
                                additional_headers={'Content-Type': 'application/json'})
            code = resp.results[0].geo_code_rs.place[0].country
            return code
        except:
            return None


    # alliance_lookup
    # String -> ResponseData
    # Gets a list of airlines for a given alliance
    def alliance_lookup(self, alliance_code):
        if alliance_code not in ['*A', '*O', '*S']:
            return None
        else:
            resp = self.request('GET',
                                sabre_endpoints['alliance_lookup'],
                                { 'alliancecode': alliance_code })
            return resp

    # equipment_lookup
    # String -> String
    # Returns the aircraft name associated with a specified IATA aircraft equipment code
    def equipment_lookup(self, aircraft_code):
        resp = self.request('GET',
                            sabre_endpoints['equipment_lookup'],
                            { 'aircraftcode': aircraft_code })
        try:
            return resp.aircraft_info[0].aircraft_name
        except:
            return None

    # multi_city_airport_lookup
    # String -> ResponseData
    # Returns the cities in a given country (supplied as a two-letter country code)
    def multi_city_airport_lookup(self, country_code):
        resp = self.request('GET',
                            sabre_endpoints['multi_city_airport_lookup'],
                            { 'country': country_code })
        return resp
