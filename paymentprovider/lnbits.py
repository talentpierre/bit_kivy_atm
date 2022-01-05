import config
import requests


def get_new_payreq_information(amount):
    '''It requests a withdraw link and returns its details.'''
    title = 'bit_kivy_atm - lnbits'
    url = f"{config.LNBITS_URL}/withdraw/api/v1/links"
    payload = {
        "title": title,
        "min_withdrawable": amount,
        "max_withdrawable": amount,
        "uses": 1,
        "wait_time": 1,
        "is_unique": True
    }
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": f"{config.LNBITS_ADMIN_KEY}"
    }
    response = requests.request("POST", url, json=payload, headers=headers).json()
    lnurl = response['lnurl']
    config.withdraw_id = response['id']
    return lnurl


def get_payment_status():
    '''It requests the paymentstatus.'''
    url = f"{config.LNBITS_URL}/withdraw/api/v1/links/{config.withdraw_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": f"{config.LNBITS_INVOICE_KEY}"
    }
    response = requests.request("GET", url, headers=headers).json()
    was_used = response['used']
    return was_used
