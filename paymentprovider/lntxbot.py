import json
import config
import requests


def _get_available_balance():
    '''It requests the available balance and returns it.'''
    url = f"{config.LNTXBOT_URL}/balance"
    headers = {"Authorization": f"Basic {config.LNTXBOT_ADMIN_KEY}"}
    response = requests.post(url, headers=headers).json()
    available_balance = response['BTC']['AvailableBalance']
    return available_balance


def get_new_payreq_information(amount):
    '''It requests a withdraw link and returns its details.'''
    url = f"{config.LNTXBOT_URL}/generatelnurlwithdraw"
    payload = {
        "satoshis": f"{amount}"
    }
    headers = {"Authorization": f"Basic {config.LNTXBOT_ADMIN_KEY}"}
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers).json()
    lnurl = response['lnurl']
    config.start_balance = _get_available_balance()
    return lnurl


def get_payment_status():
    '''It requests the paymentstatus.'''
    current_balance = _get_available_balance()
    if current_balance < config.start_balance:
        return True
    return False
