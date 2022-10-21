from peewee import *
from . import database


class BaseModel(Model):
    class Meta:
        database = database
