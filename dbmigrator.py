from datetime import datetime
from playhouse.migrate import *
from models import *

LATEST_META_VERSION = 23


class DBMigrator:
    def get_migrator(self):
        return PostgresqlMigrator(database)

    def migrate_from(self, version):
        if version == 0:
            LoginLogRecord.drop_table(fail_silently=True)
            SocialLoginRecord.drop_table(fail_silently=True)
            SocialDetails.create_table(fail_silently=True)
            LoginRecord.create_table(fail_silently=True)

            DBMeta.create_table(fail_silently=True)
            meta = DBMeta(version=1)
            meta.save()
            version += 1

        if version == 1:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(LoginRecord._meta.db_table, 'ua_browser', CharField(null=True)),
                migrator.add_column(LoginRecord._meta.db_table, 'ua_platform', CharField(null=True)),
                migrator.add_column(LoginRecord._meta.db_table, 'ua_string', CharField(null=True)),
                migrator.add_column(LoginRecord._meta.db_table, 'ua_version', CharField(null=True))
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 2:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(User._meta.db_table, 'creation_dt', DateTimeField(default=datetime.utcnow))
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 3:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(User._meta.db_table, 'contact_name', CharField(null=True)),
                migrator.add_column(User._meta.db_table, 'contact_phone', CharField(null=True)),
                migrator.add_column(User._meta.db_table, 'contact_email', CharField(null=True))
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 4:
            migrator = self.get_migrator()
            migrate(
                migrator.drop_column(User._meta.db_table, 'contact_name'),
                migrator.drop_column(User._meta.db_table, 'contact_phone'),
                migrator.drop_column(User._meta.db_table, 'contact_email')
            )
            Client.create_table(fail_silently=True)
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 5:
            Client.drop_table()
            Client.create_table(fail_silently=True)
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))
        if version == 6:
            migrator = self.get_migrator()
            # adding identity column with null=True
            if 'identity' not in Hotspot._meta.columns.keys():
                migrate(
                    migrator.add_column(Hotspot._meta.db_table, 'identity', CharField(unique=True, null=True))
                )

            # adding default identity strings
            for hotspot in Hotspot.select().where(Hotspot.identity is None):
                hotspot.identity = ''.join(e for e in hotspot.name if e.isalnum())
                hotspot.save()

            # dropping null=True on identity
            migrate(
                migrator.add_not_null(Hotspot._meta.db_table, 'identity')
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 7:
            PublicationImage.create_table(fail_silently=True)
            VKPublication.create_table(fail_silently=True)
            FacebookPublication.create_table(fail_silently=True)
            OKPublication.create_table(fail_silently=True)
            TwitterPublication.create_table(fail_silently=True)
            GooglePlusPublication.create_table(fail_silently=True)
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 8:
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 9:
            RegistrationToken.create_table(fail_silently=True)
            SMSLoginToken.create_table(fail_silently=True)
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 10:
            Balance.create_table(fail_silently=True)

            migrator = self.get_migrator()

            migrate(
                migrator.add_column(User._meta.db_table,
                                    'client_profile_id',
                                    ForeignKeyField(Client, field=Client.id, null=True)
                                    ),
                migrator.add_column(Client._meta.db_table,
                                    'balance_id',
                                    ForeignKeyField(Balance, field=Balance.id, null=True)
                                    )
            )

            for client in Client.select():
                if client.account is not None:
                    account = client.account
                    account.client_profile = client
                    account.client_profile.save()
                    account.save()

                    if client.balance is None:
                        client.balance = Balance()
                        client.balance.save()
                        client.save()

            for user in User.select():
                if user.client_profile is None:
                    c = Client()
                    c.save()
                    user.client_profile = c
                    user.save()

                    a = Account()
                    c.account = a
                    c.save()

            migrate(
                migrator.add_not_null(User._meta.db_table, 'client_profile_id'),
                migrator.add_not_null(Client._meta.db_table, 'balance_id')
            )
            if 'account' in Client._meta.columns.keys():
                migrate(
                    migrator.drop_column(Client._meta.db_table, 'account')
                )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 11:
            migrator = self.get_migrator()

            Appearance.create_table(fail_silently=True)

            print('Adding appearance_id to Hotpsot table')
            migrate(
                migrator.add_column(Hotspot._meta.db_table,
                                    'appearance_id',
                                    ForeignKeyField(Appearance, field=Appearance.id, null=True)
                                    ),
            )

            for hs in Hotspot.select():
                if hs.appearance is None:
                    print('Adding appearance for hotspot {0} owned by {1}'.format(hs.name, hs.owner.login))
                    hs_appearance = Appearance()
                    hs_appearance.save()
                    hs.appearance = hs_appearance
                    hs.save()
                else:
                    print('Hotspot {0} owned by {1} already has appearance'.format(hs.name, hs.owner.login))

            migrate(
                migrator.add_not_null(Hotspot._meta.db_table, 'appearance_id'),
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 12:
            HS_mac_phone_pair.create_table()
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 13:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(Appearance._meta.db_table, 'logo_image_filename', CharField(null=True)),
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 14:
            SMSUsageStat.create_table(fail_silently=True)
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 15:
            VpnUser.create_table(fail_silently=True)

            migrator = self.get_migrator()
            migrate(
                migrator.add_column(Hotspot._meta.db_table,
                                    'vpn_user_id',
                                    ForeignKeyField(VpnUser, field=VpnUser.id, null=True)
                                    )
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 16:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(VpnUser._meta.db_table, 'address', IntegerField(unique=True, null=True))
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 17:
            migrator = self.get_migrator()
            migrate(
                migrator.drop_not_null(Hotspot._meta.db_table, 'identity'),
                migrator.drop_not_null(Hotspot._meta.db_table, 'hostname'),
                migrator.drop_not_null(Hotspot._meta.db_table, 'port')
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 18:
            Product.create_table(fail_silently=True)
            Order.create_table(fail_silently=True)
            OrderItem.create_table(fail_silently=True)

            migrator = self.get_migrator()
            migrate(
                migrator.add_column(Hotspot._meta.db_table, 'paid_until', DateField(null=True))
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 19:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(Order._meta.db_table, 'cancelled', BooleanField(default=False)),
                migrator.add_column(
                    OrderItem._meta.db_table,
                    'client_id',
                    ForeignKeyField(User, field=User.id, null=True, backref='basket')),
                migrator.drop_not_null(OrderItem._meta.db_table, 'order_id'),
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 20:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(Product._meta.db_table, 'unit', CharField(null=False, default='piece')),
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 21:
            migrator = self.get_migrator()
            migrate(
                migrator.drop_column(Client._meta.db_table, 'balance_id')
            )
            Balance.drop_table()

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 22:
            OrganisationInfo.create_table(fail_silently=True)

            migrator = self.get_migrator()
            migrate(
                migrator.add_column(
                    User._meta.db_table,
                    'organisation_info_id',
                    ForeignKeyField(OrganisationInfo, field=OrganisationInfo.id, null=True))
            )

            for user in User.select():
                oi = OrganisationInfo()
                oi.save()

                user.organisation_info = oi
                user.save()

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 23:
            migrator = self.get_migrator()
            migrate(
                migrator.drop_column(Client._meta.db_table, 'contact_email')
            )

            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 24:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(
                    Hotspot._meta.db_table,
                    'preferred_language',
                    CharField(default="auto"))
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 25:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(
                    HS_mac_phone_pair._meta.db_table,
                    'validated',
                    BooleanField(default=False)),
                migrator.add_column(
                    Hotspot._meta.db_table,
                    'authentication_method',
                    CharField(default='sms'))
            )
            version = self.increment_meta()
            HS_mac_phone_pair.update(validated=True).execute()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 26:
            migrator = self.get_migrator()
            migrate(
                migrator.add_index(
                    LoginRecord._meta.table_name,
                    ('datetime',)
                ),
                migrator.add_index(
                    LoginRecord._meta.table_name,
                    ('phone',)
                )
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))

        if version == 27:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(
                    Hotspot._meta.table_name,
                    'socials_enabled',
                    BooleanField(default=False)
                )
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))
        if version == 28:
            migrator = self.get_migrator()
            migrate(
                migrator.add_column(
                    Hotspot._meta.table_name,
                    'redirection_url',
                    CharField(null=True)
                )
            )
            version = self.increment_meta()
            print('Migrated to version {0} successfully.'.format(version))
        else:
            print('Your DB is up to date.')

    def migrate_up(self):
        version = self._get_current_version()
        self.migrate_from(version)

    def increment_meta(self):
        meta = DBMeta.get(DBMeta.id == 1)
        meta.version += 1
        meta.save()
        return meta.version

    def _get_current_version(self):
        if DBMeta.table_exists():
            return DBMeta.get(DBMeta.id == 1).version
        else:
            return 0
