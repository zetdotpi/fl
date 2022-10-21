from datetime import datetime, timedelta
from peewee import *
from . import BaseModel

EXPIRATION_PERIOD = 90  # in days
FRESH_PERIOD = 3600     # in seconds, full hour


class HS_mac_phone_pair(BaseModel):
    mac = CharField(primary_key=True)
    phone = CharField()
    validated = BooleanField(default=False)
    valid_until = DateTimeField(default=datetime.utcnow() + timedelta(days=EXPIRATION_PERIOD))

    def is_valid(self):
        return not self.is_outdated() and self.validated

    def is_outdated(self):
        return self.valid_until < datetime.utcnow()

    def _created(self):
        return self.valid_until - timedelta(days=EXPIRATION_PERIOD)

    def is_fresh(self):
        return datetime.utcnow() - self._created() < timedelta(seconds=FRESH_PERIOD)
