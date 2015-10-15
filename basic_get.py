import requests
import json
import base64


def read_config():
    raw_data = open('config.json').read()

    data = json.loads(raw_data)

    client_secret = data['sabre_client_secret']
    client_id = data['sabre_client_id']

    return (client_id, client_secret)


def get_token(client_id, client_secret):
    encoded = str(base64.b64encode(client_id)) + ':' + str(base64.b64encode(client_secret))

    encoded = str(base64.b64encode(encoded))

    headers = {
        'Authorization': 'Basic ' + encoded,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        'grant_type': 'client_credentials'
    }

    data = requests.post('https://api.test.sabre.com/v2/auth/token',
                         headers=headers,
                         data=payload)

    return data


def main():
    cid, secret = read_config()
    data = get_token(cid, secret)
    print(data.json())


if __name__ == "__main__":
    main()
