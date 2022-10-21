from peewee import *
from . import BaseModel


class HS_Device(BaseModel):
    mac = CharField(primary_key=True)
