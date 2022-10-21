import string
from random import choice

token_chars = string.ascii_letters + string.digits
sms_chars = string.digits


def generate_token(length=16):
    return ''.join([choice(token_chars) for _ in range(length)])


def generate_smstoken(length=4, unique=True):
    return ''.join([choice(sms_chars) for _ in range(length)])


# random utils for models store
_24 = 2**24
_16 = 2**16
_8 = 2**8


def ip_to_integer(ip):
    '''
    Converts IPv4 string (like 127.0.0.1) to integer.
    Use it to store IP addresses in database as integer fields (32 bits)
    '''
    octets = [int(part) for part in ip.split('.')]
    return octets[0] * _24 + octets[1] * _16 + octets[2] * _8 + octets[3]


def ip_from_integer(value):
    '''Converts integer to IPv4 string (like 127.0.0.1)'''
    res = value
    o1 = res // _24
    res -= o1 * _24
    o2 = res // _16
    res -= o2 * _16
    o3 = res // _8
    o4 = res - o3 * _8

    return '{0}.{1}.{2}.{3}'.format(o1, o2, o3, o4)
