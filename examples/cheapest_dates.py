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
    if (len(sys.argv) < 4):
        print('Specify origin, destination, length of stay, ' +
              'and optionally point of sale')
    else:
        client = set_up_client()
        origin = sys.argv[1]
        destination = sys.argv[2]

        try:
            length_of_stay = [int(sys.argv[3]),]
        except:
            print('Length of stay must be an integer')

        if len(sys.argv) >= 5:
            point_of_sale = sys.argv[4]
        else:
            point_of_sale = 'US'

        try:
            resp = client.lead_price(origin, destination, length_of_stay,
                                     point_of_sale=point_of_sale)
        except sabre_exceptions.SabreErrorNotFound:
            print('No results were found')
            sys.exit(0)

        prices = []
        for fare in resp.fare_info:
            if fare.lowest_fare != 'N/A':
                prices.append((fare.departure_date_time,
                               fare.return_date_time,
                               fare.lowest_fare.fare,
                               fare.lowest_fare.airline_codes,))

        sorted_prices = sorted(prices, key = lambda x: x[2])

        print('Lowest 20 prices:')
        for price in sorted_prices[:20]:
            price_round = '%.2f' % price[2]
            out_str = "${0:8} {1:8} {2} to {3}".format(price_round,
                                                       ' '.join(price[3]),
                                                       price[0].split('T')[0],
                                                       price[1].split('T')[0])
            print(out_str)


if __name__ == '__main__':
    main()
