from peewee import *
from . import BaseModel, Hotspot
# for login using login/password pair


class HotspotUser(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='users')
    login = CharField()
    password = CharField()
