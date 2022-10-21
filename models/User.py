from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import *
from . import BaseModel, Client, OrganisationInfo


class User(BaseModel):
    login = CharField(unique=True)
    pwd_hash = CharField()
    creation_dt = DateTimeField(default=datetime.utcnow)
    client_profile = ForeignKeyField(Client, on_delete='CASCADE')
    organisation_info = ForeignKeyField(OrganisationInfo, null=True, on_delete='CASCADE')

    role = CharField(default='user')

    def set_password(self, password):
        self.pwd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwd_hash, password)

    def is_active(self):
        return self.pwd_hash is not None and self.pwd_hash != 'prereg'

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.login

    def as_dict(self):
        return {
            # 'id': self.id,
            'email': self.login,
            'role': self.role,
            'profile': self.client_profile.as_dict(),
            'organisationInfo': self.organisation_info.as_dict()
        }
