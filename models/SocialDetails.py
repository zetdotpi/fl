from peewee import *
from . import BaseModel


class SocialDetails(BaseModel):
    net_name = CharField()
    net_id = CharField()
    name = CharField(null=True)
    surname = CharField(null=True)
