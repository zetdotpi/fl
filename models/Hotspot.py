import os
from datetime import date, datetime, timedelta
from peewee import *
from . import BaseModel, Appearance, User, VpnUser


class Hotspot(BaseModel):
    '''
    name -- descriptive name
    identity -- identification string, starts with letter includes (uppercase letters, lowercase letters, numbers).
    hostname -- IP address or domain name (can use DynDNS)
    port -- SSH port
    owner -- user, that can manage hotspot
    note -- description (any info). For admins only
    '''
    name = CharField()
    identity = CharField(unique=False, null=True)
    hostname = CharField(null=True)
    port = IntegerField(default=8728, null=True)
    owner = ForeignKeyField(User, backref='hotspots')
    note = TextField(null=True)

    station_id = CharField(null=True)                                # mac address, formatted 'XX:XX:XX:XX:XX:XX'
    location_id = CharField(null=True)                               # string, set manually
    location_name = CharField(null=True)                             # string, set manually
    appearance = ForeignKeyField(Appearance, backref='hotspot', null=False)

    # available methods are ['sms', 'call']
    authentication_method = CharField(default='call')
    preferred_language = CharField(default="auto")
    vpn_user = ForeignKeyField(VpnUser, null=True)
    paid_until = DateField(null=True)

    socials_enabled = BooleanField(default=False)
    redirection_url = CharField(null=True)

    def has_logo(self):
        return self.appearance.logo_image_filename is not None

    def logo_static_path(self):
        return os.path.join('clients', self.identity, self.appearance.logo_image_filename)

    def current_publications(self):
        current_pubs = {
            'vk': self.publications_vk[0] if self.publications_vk.count() > 0 else None,
            'facebook': self.publications_facebook[0] if self.publications_facebook.count() > 0 else None,
            'ok': self.publications_ok[0] if self.publications_ok.count() > 0 else None,
            'twitter': self.publications_twitter[0] if self.publications_twitter.count() > 0 else None,
            'googleplus': self.publications_googleplus[0] if self.publications_googleplus.count() > 0 else None
        }
        return current_pubs

    def unique_visitors(self, days=0):
        # HACK: dirty import
        from . import LoginRecord
        since = date.today() - timedelta(days=days)
        # query = self.logins_log.select(LoginRecord.phone).distinct().where(LoginRecord.datetime >= since)
        # print(query.sql())
        # return LoginRecord.select(LoginRecord.phone).distinct().where(LoginRecord.datetime >= since).count()
        return self.logins_log.select(LoginRecord.phone).distinct().where(LoginRecord.datetime >= since).count()

    def stats(self, days=7):
        # HACK: dirty import
        from . import LoginRecord
        stats = LoginRecord.select(
            fn.DATE(LoginRecord.datetime).alias('day'),
            fn.COUNT(LoginRecord.id).alias('count'))\
            .group_by(fn.DATE(LoginRecord.datetime))\
            .join(Hotspot)\
            .where(Hotspot.id == self.id, LoginRecord.datetime >= datetime.today() - timedelta(days=days))\
            .order_by(fn.DATE(LoginRecord.datetime))\
            .group_by(fn.DATE(LoginRecord.datetime))\
            .desc()

        result = {}
        for s in stats:
            # print(s.day, s.count)
            result[s.day] = s.count

        for day in range(days):
            dt = datetime.now() - timedelta(day)
            d = date(dt.year, dt.month, dt.day)

            if result.get(d) is None:
                result[d] = 0

        return [{'day': key, 'count': result[key]} for key in sorted(result)]

    def as_dict(self, detailed=False):
        data = {
            'name': self.name,
            'identity': self.identity,
            'hostname': self.hostname,
            'port': self.port,
            'owner': self.owner.login,
            'note': self.note,
            'appearance': self.appearance.as_dict(),
            'overview': {},
            'visitors': {
                'today': self.unique_visitors(),
                'week': self.unique_visitors(7),
                'month': self.unique_visitors(30)
            }
        }
        if self.vpn_user is not None:
            data['vpnUser'] = self.vpn_user.as_dict()
        if self.paid_until is not None:
            data['paidUntil'] = self.paid_until.isoformat()

        return data

    def logins_count_24_hours(self):
        from . import LoginRecord
        logins_count = LoginRecord.select().where(LoginRecord.hotspot == self,
                                                  LoginRecord.datetime >= datetime.today() - timedelta(days=1)).count()
        return str(logins_count)

    def select_phone_logins(self):
        from . import LoginRecord
        return self.logins_log.where(LoginRecord.method == 'phone')

    def select_social_logins(self):
        from . import LoginRecord
        return self.logins_log.where(LoginRecord.method == 'social')
