from peewee import *
from . import BaseModel, Hotspot


class TwitterPublication(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='publications_twitter')
    text = CharField()
    hashtags = CharField(null=True)
