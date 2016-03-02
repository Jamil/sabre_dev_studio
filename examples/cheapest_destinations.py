'''
Finds the cheapest fares filed to a given city

Example:
    python cheapest-destinations.py YTO

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

def main():
    if (len(sys.argv) < 2):
        print('Please specify IATA city or airport code as a command-line argument')
    elif (len(sys.argv[1]) != 3):
        print('IATA city or airport code must be 3 letters long')
    else:
        client = set_up_client()
        city = sys.argv[1]

        try:
            point_of_sale = sys.argv[2]
            resp = client.flights_to(city, point_of_sale)
        except IndexError:
            resp = client.flights_to(city)

        data = resp[0]
        for city in data:
            airlines = ' '.join(city.lowest_fare.airline_codes)
            lowest_fare = str('${:,.2f}'.format(city.lowest_fare.fare))

            dep_date = datetime.datetime.strptime(city.departure_date_time,
                                                  "%Y-%m-%dT%H:%M:%S")
            arr_date = datetime.datetime.strptime(city.return_date_time,
                                                  "%Y-%m-%dT%H:%M:%S")

            dep_date_str = dep_date.strftime('%b %d')
            arr_date_str = arr_date.strftime('%b %d')

            data = "{0:4} {1:11} {2:12} {3:8} to {4:8}".format(city.origin_location,
                                                               lowest_fare,
                                                               airlines,
                                                               dep_date_str,
                                                               arr_date_str)
            print data

if __name__ == '__main__':
    main()
