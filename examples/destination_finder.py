'''
Finds the cheapest fares filed FROM a given city

Example:
    python cheapest-destinations.py SFO

Result:
    FLL 165.62
    MCO 165.62
    JFK 172.36
    LGA 191.12
'''

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

def read_config():
    raw_data = open('config.json').read()

    data = json.loads(raw_data)

    client_secret = data['sabre_client_secret']
    client_id = data['sabre_client_id']

    return (client_id, client_secret)

def set_up_client():
    # Read from config
    client_id, client_secret = read_config()
    sds = sabre_dev_studio.SabreDevStudio()
    sds.set_credentials(client_id, client_secret)
    sds.authenticate()
    return sds

def parse_args(argv):
    city = sys.argv[1]
    point_of_sale = sys.argv[2]
    return (city,point_of_sale)

def main():
    if (len(sys.argv) < 2):
        print('Please specify IATA city or airport code as a command-line argument')
    elif (len(sys.argv[1]) != 3):
        print('IATA city or airport code must be 3 letters long')
    else:
        client = set_up_client()
        city, point_of_sale = parse_args(sys.argv)

        if point_of_sale:
            resp = client.destination_finder(city,
                                             length_of_stay=0,
                                             point_of_sale=point_of_sale)
        else:
            resp = client.destination_finder(city,
                                             length_of_stay=0)

        prices = []
        fares = resp.fare_info
        for fare in fares:
            if fare.lowest_fare != 'N/A':
                prices.append((fare.destination_location,
                               fare.lowest_fare.fare,
                               fare.lowest_fare.airline_codes,))
            
