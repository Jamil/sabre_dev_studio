'''
Finds the cheapest fares filed FROM a given city

Example:
    python cheapest-destinations.py SFO -l 0 -hf 300 -n 1

Result:
    LAS  $66.20    B6       2016-04-12 to 2016-04-12
'''

import datetime
import json
import sys
import argparse
import random

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
    parser.add_argument('-nu', '--no-unique', action='store_true',
                        help='will return duplicate cities in results', default=False)
    parser.add_argument('-n', '--num-results', type=int,
                        help='number of results to return', default=10)
    parser.add_argument('-s', '--sort-by', type=str,
                        help='which parameter to sort results by', default='price',
                        choices=['price', 'cpm', 'random'])
    parser.add_argument('-a', '--airline', type=str, nargs='*',
                        help='airline codes to search', default=None)
    parser.add_argument('-d', '--destination-city', type=str,
                        help='destination city code', default=None)
    parser.add_argument('-l', '--length-of-stay', type=int,
                        help='length of stay at destintation', default=[0], nargs='+')
    parser.add_argument('-pm', '--plus-or-minus', type=int,
                        help='if single length of stay is specified, searches within this margin (e.g. if length of stay is 3, and this value is 2, it\'ll search for length of stay values 1, 2, 3, 4, and 5)',
                        default=0)
    parser.add_argument('-cpm', '--cost-per-mile', type=float,
                        help='fare cost per mile', default=None)
    parser.add_argument('-ps', '--point-of-sale', type=str,
                        help='point of sale country', default=None)
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

    # Look up city
    city_resp = client.country_code_lookup(args.origin)

    if not city_resp:
        print("Invalid city/airport code.")
        sys.exit(0)

    if not args.point_of_sale:
        pos = city_resp
    else:
        pos = args.point_of_sale

    if len(args.length_of_stay) == 1 and args.plus_or_minus:
        los = args.length_of_stay[0]
        pm = args.plus_or_minus
        length_of_stay = list(range(max(los - pm, 0),
                                    los + pm))
    else:
        length_of_stay = args.length_of_stay

    try:
        resp = client.destination_finder(args.origin,
                                         destination=args.destination_city,
                                         length_of_stay=length_of_stay,
                                         point_of_sale=pos,
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
    except sabre_exceptions.SabreErrorNotFound:
        print("No results found.")
        sys.exit(0)
        
    prices = []
    fares = resp.fare_info
    for fare in fares:
        if fare.lowest_fare != 'N/A':
            prices.append((fare.destination_location,
                           fare.departure_date_time,
                           fare.return_date_time,
                           fare.lowest_fare.fare,
                           fare.lowest_fare.airline_codes,
                           fare.price_per_mile))

    if args.sort_by == 'price':
        sorted_prices = sorted(prices, key = lambda x: x[3])
    elif args.sort_by == 'cpm':
        sorted_prices = sorted(prices, key = lambda x: x[5])
    else:
        sorted_prices = prices
        random.shuffle(sorted_prices)
    

    count = 0
    cities = {}
    for price in sorted_prices:
        if count >= args.num_results:
            break

        airlines = price[4]

        if not args.airline:
            airline_valid = True
        else:
            intersection_airlines = set(airlines).intersection(args.airline) 
            airline_valid = len(intersection_airlines)

        if args.no_unique:
            uniqueness_valid = True
        else:
            uniqueness_valid = cities.get(price[0]) is None

        if airline_valid and uniqueness_valid:
            price_round = '%.2f' % price[3]
            cpm_round = '%.2f' % price[5]

            if args.sort_by == 'cpm' or args.cost_per_mile:
                fstring = "{0:4} ${1:8} {2:4} cpm    {3:10} {4} to {5}"
                out_str = fstring.format(price[0],
                                         price_round,
                                         cpm_round,
                                         ' '.join(airlines),
                                         price[1].split('T')[0],
                                         price[2].split('T')[0])
            else:
                fstring = "{0:4} ${1:8} {2:10} {3} to {4}"
                out_str = fstring.format(price[0],
                                         price_round,
                                         ' '.join(airlines),
                                         price[1].split('T')[0],
                                         price[2].split('T')[0])
                
            count += 1
            cities[price[0]] = True
            print(out_str)

    if count == 0:
        print("No results found.")


if __name__ == '__main__':
    main()
