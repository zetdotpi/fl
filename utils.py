import re
from pprint import pprint
import requests
import json
import base64

import config


def dbg_print(name, obj):
    print(name)
    print(40 * '=')
    pprint(obj)
    if obj is not None and hasattr(obj, '__dict__'):
        print(40 * '-')
        pprint(obj.__dict__)
    print()


MAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')
MAIL_SENDER_DEFAULT = 'mailbot@example.com'


def check_email(email):
    return re.match(MAIL_REGEX, email)


def get_sms_balance():
    if config.SMS_GATEWAY == 'prostorsms':
        cred = {
            'login': config.PROSTORSMS_LOGIN,
            'password': config.PROSTORSMS_PASSWORD
        }
        res = requests.post('http://api.prostor-sms.ru/messages/v2/balance.json', json=cred)
        return float(res.json()['balance'][0]['balance'])

    if config.SMS_GATEWAY == 'iqsms':
        cred = {
            'login': config.IQSMS_LOGIN,
            'password': config.IQSMS_PASSWORD
        }

        res = requests.post('http://api.iqsms.ru/messages/v2/balance.json', json=cred)
        pprint(res.json())
        return float(res.json()['balance'][0]['balance'])
    else:
        return None


def send_sms(phone, text):
    phonenum = str(phone.country_code) + str(phone.national_number)
    print('Trying to send sms to number {0}'.format(phonenum))
    if config.SMS_GATEWAY == 'smsaero':
        return _sms_smsaero(phone, text)
    elif config.SMS_GATEWAY == 'iqsms':
        return _sms_iqsms(phone, text)
    elif config.SMS_GATEWAY == 'prostorsms':
        return _sms_prostorsms(phone, text)
    else:
        raise NotImplementedError


def _sms_iqsms(phone, text):
    print('Using IQSMS')
    phonenum = '+' + str(phone.country_code) + str(phone.national_number)
    res = requests.post('http://json.gate.iqsms.ru/send/',
                        json={
                            'login': config.IQSMS_LOGIN,
                            'password': config.IQSMS_PASSWORD,
                            'messages':
                                [
                                    {
                                        'clientId': '1',
                                        'phone': phonenum,
                                        'text': text,
                                        'sender': 'Example'
                                    }
                                ]
                        })
    print(res.json())
    return res.json()['status'] == 'ok'


def _sms_smsaero(phone, text, digital=False):
    print('Using SMSAERO')
    phonenum = str(phone.country_code) + str(phone.national_number)
    payload = {
        'user': config.SMSAERO_LOGIN,
        'password': config.SMSAERO_PASSWORD_HASH,
        'to': phonenum,
        'from': 'Example',
        'text': text,
        'answer': 'json'
    }
    if digital:
        payload['digital'] = 1

    resp = requests.post('https://gate.smsaero.ru/send/', params=payload)
    resp_json = json.loads(resp.text)
    print('Got answer from server')
    print(40 * '=')
    pprint(resp_json)

    return resp_json['result'] == 'accepted'


def _sms_prostorsms(phone, text):
    print('Using ProstorSMS')
    phonenum = '+' + str(phone.country_code) + str(phone.national_number)
    payload = {
        'login': config.PROSTORSMS_LOGIN,
        'password': config.PROSTORSMS_PASSWORD,
        'sender': 'Example',
        'messages': [
            {
                'phone': phonenum,
                'clientId': 'none',
                'text': text
            }
        ]
    }
    resp = requests.post('http://api.prostor-sms.ru/messages/v2/send.json', json=payload)

    return resp.json()['status'] == 'ok'


# use this to send data with oauth request using state
def json_to_base64(data):
    dec_string = json.dumps(data)
    dec_bytes = bytes(dec_string, 'utf8')
    enc_bytes = base64.b64encode(dec_bytes)
    enc_string = enc_bytes.decode('utf8')
    return enc_string


def base64_to_json(enc_string):
    enc_bytes = enc_string.encode('utf8')
    dec_bytes = base64.b64decode(enc_bytes)
    dec_string = dec_bytes.decode('utf8')
    data = json.loads(dec_string)
    return data


def dict_to_state(data):
    return json_to_base64(data)

def state_to_dict(data):
    return base64_to_json(data)
