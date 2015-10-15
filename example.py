import sabre_dev_studio
import json

def test():
    cid, secret = read_config()
    sds = sabre_dev_studio.SabreDevStudio(cid, secret)
    sds.authorize()

def read_config():
    raw_data = open('config.json').read()

    data = json.loads(raw_data)

    client_secret = data['sabre_client_secret']
    client_id = data['sabre_client_id']

    return (client_id, client_secret)
