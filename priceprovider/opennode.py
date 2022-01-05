import requests


def get_btc_price():
    '''It requests the BTC/EUR price and returns it.'''
    url = 'https://api.opennode.co/v1/rates'
    response = requests.get(url).json()
    btc_price = float(response['data']['BTCEUR']['EUR'])
    return btc_price
