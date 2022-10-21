from peewee import *
from . import BaseModel


class HS_Phone(BaseModel):
    phone = CharField(primary_key=True)
