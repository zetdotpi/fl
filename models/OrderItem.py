from peewee import *
from . import BaseModel, User, Hotspot, Product, Order


class OrderItem(BaseModel):
    client = ForeignKeyField(User, backref='basket')
    order = ForeignKeyField(Order, null=True, backref='items')
    item = ForeignKeyField(Product)
    count = IntegerField(default=1)
    hotspot = ForeignKeyField(Hotspot, null=True)

    def total(self):
        return self.count * self.item.price

    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.item.name,
            'description': self.item.description,
            'price': self.item.price.to_eng_string(),
            'amount': self.count,
            'unit': self.item.unit,
            'total_price': self.total().to_eng_string(),
        }

        if self.hotspot is not None:
            data['hotspot'] = self.hotspot.identity

        return data

    def __str__(self):
        return '<OrderItem> [{oi.id}] {oi.item.name} (hs: {oi.hotspot.name}) : {oi.count} for {oi.item.price}'.format(oi=self)
