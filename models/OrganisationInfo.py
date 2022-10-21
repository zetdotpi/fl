from peewee import *
from . import BaseModel


class OrganisationInfo(BaseModel):
    name = CharField(null=True)
    inn = CharField(null=True)
    kpp = CharField(null=True)
    address = CharField(null=True)
    phone = CharField(null=True)

    def as_dict(self):
        return {
            'name': self.name,
            'inn': self.inn,
            'kpp': self.kpp,
            'address': self.address,
            'phone': self.phone
        }
