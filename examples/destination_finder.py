'''
Finds the cheapest fares filed FROM a given city

Example:
    python cheapest-destinations.py SFO

Result:
    LAS  $66.20    B6       2016-04-12 to 2016-04-12
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
    try:
        point_of_sale = sys.argv[2]
    except:
        point_of_sale = 'US'
    return (city,point_of_sale)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                                           help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                                           const=sum, default=max,
                                           help='sum the integers (default: find the max)')

    client = set_up_client()

    args = parser.parse_args()

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
                           fare.departure_date_time,
                           fare.return_date_time,
                           fare.lowest_fare.fare,
                           fare.lowest_fare.airline_codes,))

    sorted_prices = sorted(prices, key = lambda x: x[3])

    print('Lowest 20 prices:')
    for price in sorted_prices[:20]:
        price_round = '%.2f' % price[3]
        out_str = "{0:4} ${1:8} {2:8} {3} to {4}".format(price[0],
                                                         price_round,
                                                         ' '.join(price[4]),
                                                         price[1].split('T')[0],
                                                         price[2].split('T')[0])
        print(out_str)


if __name__ == '__main__':
main()
