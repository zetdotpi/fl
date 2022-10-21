from datetime import datetime
from peewee import *
from . import BaseModel, Hotspot, SocialDetails


class LoginRecord(BaseModel):
    class Meta:
        order_by = ('-datetime',)
    datetime = DateTimeField(default=datetime.utcnow)
    hotspot = ForeignKeyField(Hotspot, null=True, backref='logins_log')
    method = CharField()
    phone = CharField(null=True)
    social = ForeignKeyField(SocialDetails, null=True)
    access_token = CharField()

    # service info
    ua_browser = CharField(null=True)
    ua_platform = CharField(null=True)
    ua_string = CharField(null=True)
    ua_version = CharField(null=True)
