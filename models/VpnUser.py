from peewee import *

import config
from . import BaseModel
from .utils import ip_from_integer


class VpnUser(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    address = IntegerField(unique=True)

    def get_ip_string(self):
        return ip_from_integer(self.address)

    @staticmethod
    def get_new_ip():
        if VpnUser.select(fn.Max(VpnUser.address)).scalar() is not None:
            return VpnUser.select(fn.Max(VpnUser.address)).scalar() + 1
        else:
            return config.VPN_POOL_MIN_INTEGER

    def as_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'address': self.get_ip_string()
        }
