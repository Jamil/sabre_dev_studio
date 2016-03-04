import time
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

def process_args():
    origin_city = sys.argv[1]
    destination_city = sys.argv[2]
    departure_time_obj = time.strptime(sys.argv[3], '%m-%d-%Y')
    departure_date = datetime.datetime(*departure_time_obj[0:6])
    carrier = sys.argv[4]
    flt_num = sys.argv[5]
    return origin_city, destination_city, departure_date, carrier, flt_num

def print_cabin(cabin_data):
    rows = cabin_data.row
    cabin_name = cabin_data.cabin_class.cabin_type.content

    print('-' * len(cabin_name))
    print(cabin_name)
    print('-' * len(cabin_name))

    cabin_layout = cabin_data.column
    layout_str = ''
    next_aisle_cols = []

    for i in range(0, len(cabin_layout)):
        if ('Aisle' in cabin_layout[i].characteristics):
            if i == 0 or ('Aisle' not in (cabin_layout[i-1].characteristics)):
                layout_str += cabin_layout[i].column + '   '
                next_aisle_cols.append(cabin_layout[i].column)
            else:
                layout_str += cabin_layout[i].column + ' '
        else:
            layout_str += cabin_layout[i].column + ' '
    print('  \t' + layout_str)

    for row in rows:
        row_num = row.row_number
        seat_str = str(row_num) + '\t'
        for seat in row.seat:
            if seat.occupied_ind:
                seat_str += 'X '
            else:
                seat_str += '- '
            if (seat.number in next_aisle_cols):
                seat_str += '  '
        print(seat_str)

    print('')
    
def main():
    if (len(sys.argv) < 6):
        print('Please specify all arguments; origin IATA airport code, destination IATA airport code, departure date (MM-DD-YYYY), carrier (2-digit), and flight number')
    else:
        client = set_up_client()

        orig, dest, dep, carrier, flt = process_args()

        resp = client.seat_map(orig, dest, dep, carrier, flt)

        cabins = resp.enhanced_seat_map_rs.seat_map[0].cabin

        for cabin in cabins:
            print_cabin(cabin)


if __name__ == '__main__':
    main()
