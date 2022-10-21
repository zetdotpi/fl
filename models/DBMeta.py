from peewee import *
from . import BaseModel


class DBMeta(BaseModel):
    version = IntegerField()
