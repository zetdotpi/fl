from peewee import *
from playhouse.postgres_ext import *
from . import BaseModel, Hotspot, HS_Phone


class HS_AuthRecord(BaseModel):
    hotspot = ForeignKeyField(Hotspot)
    phone = ForeignKeyField(HS_Phone)
    social = JSONField(null=True)
