from peewee import *
from . import BaseModel, Hotspot, PublicationImage


class FacebookPublication(BaseModel):
    class Meta:
        order_by = ('-id',)
    hotspot = ForeignKeyField(Hotspot, backref='publications_facebook')
    text = TextField()
    image_caption = CharField(null=True)
    image = ForeignKeyField(PublicationImage, null=True)
