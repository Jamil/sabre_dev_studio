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
import argparse

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

def convert_date(d):
    if d is not None:
        return datetime.datetime.strptime(d, '%m-%d-%Y')
    else:
        return None

def parse_args(argv):
    city = sys.argv[1]
    try:
        point_of_sale = sys.argv[2]
    except:
        point_of_sale = 'US'
    return (city,point_of_sale)

def main():
    parser = argparse.ArgumentParser(description='Get destinations and fares given certain parameters.')
    parser.add_argument('origin', type=str, help='departure city code')
    parser.add_argument('-u', '--unique-only', action='store_true',
                        help='only return unique cities in results', default=True)
    parser.add_argument('-n', '--num-results', type=int,
                        help='number of results to return', default=10)
    parser.add_argument('-d', '--destination-city', type=str,
                        help='destination city code', default=None)
    parser.add_argument('-l', '--length-of-stay', type=int,
                        help='length of stay at destintation', default=0, nargs='+')
    parser.add_argument('-p', '--cost-per-mile', type=float,
                        help='fare cost per mile', default=None)
    parser.add_argument('-s', '--point-of-sale', type=str,
                        help='point of sale country', default='US')
    parser.add_argument('-lf', '--lowest-fare', type=int,
                        help='minimum fare to return', default=None)
    parser.add_argument('-hf', '--highest-fare', type=int,
                        help='maximum fare to return', default=None)
    parser.add_argument('-r', '--region', type=str,
                        help='region to search', default=None, 
                        choices=['Africa',
                                 'Asia Pacific',
                                 'Europe',
                                 'Latin America',
                                 'Middle East',
                                 'North America'],
                        nargs='*')
    parser.add_argument('-t', '--theme', type=str,
                        help='region to search', default=None, 
                        choices=['beach', 'disney', 'gambling', 'historic',
                                 'mountains', 'national-parks', 'outdoors',
                                 'romantic', 'shopping', 'skiing',
                                 'theme-park', 'caribbean'],
                        nargs='*')
    parser.add_argument('-c', '--country', type=str,
                        help='only returns results from this country code',
                        default=None)
    parser.add_argument('-dd', '--departure-date', type=str,
                        help='earliest departure date (MM-DD-YYYY)',
                        default=None)
    parser.add_argument('-rd', '--return-date', type=str,
                        help='earliest return date (MM-DD-YYYY)',
                        default=None)
    parser.add_argument('-edd', '--earliest-departure', type=str,
                        help='earliest departure date (MM-DD-YYYY)',
                        default=None)
    parser.add_argument('-erd', '--earliest-return', type=str,
                        help='earliest return date (MM-DD-YYYY)',
                        default=None)
    args = parser.parse_args()

    client = set_up_client()

    resp = client.destination_finder(args.origin,
                                     destination=args.destination_city,
                                     length_of_stay=args.length_of_stay,
                                     point_of_sale=args.point_of_sale,
                                     departure_date=convert_date(args.departure_date),
                                     return_date=convert_date(args.return_date),
                                     earliest_return_date=
                                        convert_date(args.earliest_return),
                                     earliest_departure_date=
                                        convert_date(args.earliest_departure),
                                     min_fare=args.lowest_fare,
                                     max_fare=args.highest_fare,
                                     region=args.region,
                                     theme=args.theme,
                                     location=args.country,
                                     cost_per_mile=args.cost_per_mile)

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

    count = 0
    cities = {}
    for price in sorted_prices:
        if count >= args.num_results:
            break
        if not args.unique_only or not cities.get(price[0]):
            price_round = '%.2f' % price[3]
            out_str = "{0:4} ${1:8} {2:8} {3} to {4}".format(price[0],
                                                             price_round,
                                                             ' '.join(price[4]),
                                                             price[1].split('T')[0],
                                                             price[2].split('T')[0])
            count += 1
            cities[price[0]] = True
            print(out_str)


if __name__ == '__main__':
    main()
