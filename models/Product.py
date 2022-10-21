from peewee import *
from . import BaseModel


class Product(BaseModel):
    name = CharField(unique=True)
    description = CharField(null=True)
    price = DecimalField(decimal_places=2)
    unit = CharField(null=False, default='piece')

    def __str__(self):
        return '<Product> [{p.id}] {p.name}: {p.description}'.format(p=self)
