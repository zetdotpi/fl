from peewee import *
from . import BaseModel, Hotspot, PublicationImage


class VKPublication(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='publications_vk')
    text = TextField()
    image = ForeignKeyField(PublicationImage, null=True)
