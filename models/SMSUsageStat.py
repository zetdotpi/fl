from datetime import date
from peewee import *
from . import BaseModel, Hotspot


class SMSUsageStat(BaseModel):
    hotspot = ForeignKeyField(Hotspot, null=False, backref='sms_usage_stats')
    date = DateField(default=date.today())
    count = IntegerField(default=0)

    class Meta:
        order_by = ('date',)
