from peewee import *
from . import BaseModel


class Client(BaseModel):
    contact_name = CharField(null=True)
    contact_phone = CharField(null=True)
    # contact_email = CharField(null=True)

    def as_dict(self):
        return {
            'name': self.contact_name,
            'phone': self.contact_phone
            # 'email': self.contact_email
        }
