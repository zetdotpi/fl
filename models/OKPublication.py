from peewee import *
from . import BaseModel, Hotspot


class OKPublication(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='publications_ok')
    url = CharField()
