from peewee import *
from . import BaseModel, Hotspot


class SMSLoginToken(BaseModel):
    hotspot = ForeignKeyField(Hotspot)
    phone = CharField()
    value = CharField(unique=True)
    valid = BooleanField(default=True)
