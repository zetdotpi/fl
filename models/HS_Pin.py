from datetime import datetime
from peewee import *
from . import BaseModel, HS_Phone, HS_Device


class HS_Pin(BaseModel):
    phone = ForeignKeyField(HS_Phone)
    device = ForeignKeyField(HS_Device)
    value = CharField()
    issue_dt = DateTimeField(default=datetime.utcnow)
    activation_dt = DateTimeField(null=True)
