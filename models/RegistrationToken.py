from peewee import *
from . import BaseModel, User


class RegistrationToken(BaseModel):
    value = CharField()
    user = ForeignKeyField(User, backref='reg_token')
    valid = BooleanField(default=True)
