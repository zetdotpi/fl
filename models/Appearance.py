# import os
from peewee import *
from . import BaseModel


class Appearance(BaseModel):
    title = CharField(default='Example')
    text = CharField(null=True)
    background_image = CharField(null=True)
    logo_image_filename = CharField(null=True)

    def as_dict(self):
        return {
            'title': self.title,
            'text': self.text,
            'logo_absolute_path': 'http://login.example.com/static/clients/{identity}/{filename}'.format(
                identity=self.hotspot.get().identity,
                filename=self.logo_image_filename) if self.logo_image_filename else None
        }
