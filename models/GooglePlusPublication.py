from peewee import *
from . import BaseModel, Hotspot


class GooglePlusPublication(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='publications_googleplus')
    url = CharField()
