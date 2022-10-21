from flask.ext.script import Manager
from app import app, database
from models import *
from dbmigrator import DBMigrator, LATEST_META_VERSION
from getpass import getpass


def create_user(email, password, admin=False):
    if User.select().where(User.login == email).count() > 0:
        return User.get(User.login == email)

    u = User(login=email)
    u.set_password(password)
    if admin:
        u.role = 'admin'

    c = Client()
    c.save()

    u.client_profile = c
    u.save()

    return u


def create_hotspot(name, hostname, owner):
    appearance = Appearance()
    appearance.save()
    hs = Hotspot(name=name, identity=name, hostname=hostname, owner=owner, appearance=appearance)
    hs.save()
    return hs


def create_product(name, description, price):
    product = Product(name=name, description=description, price=price)
    product.save()
    return product


manager = Manager(app)


@manager.command
def populate_products():
    'Creates default products (100 SMS Package, 500 SMS Package, 1000 SMS Package, Monthly service)'
    create_product('100 SMS Pack', '', 250)
    create_product('500 SMS Pack', '', 1250)
    create_product('1000 SMS Pack', '', 2500)


@manager.command
def migrate_up():
    'Migrates DB scheme to current'
    d = DBMigrator()
    d.migrate_up()


@manager.command
def setup():
    'Create DB scheme and add admin user'

    print('Creating tables')
    database.create_tables(
        [
            DBMeta,
            Client,
            User,
            Appearance,
            Hotspot,
            HotspotUser,
            SocialDetails,
            LoginRecord,
            PublicationImage,
            VKPublication,
            FacebookPublication,
            OKPublication,
            TwitterPublication,
            GooglePlusPublication,
            RegistrationToken,
            SMSLoginToken,
            SMSUsageStat,
            VpnUser,
            Product,
            Order,
            OrderItem
        ],
        safe=True
    )
    print()
    print("Now it's time to create admin account")
    username = str(input("Email: "))
    password = getpass()
    u = User(login=username)
    u.set_password(password)
    u.role = 'admin'

    client = Client()
    print('saving client_profile')
    client.save()

    u.client_profile = client
    print('saving user')
    u.save()
    print("Ok, done.")

    print("Setting up DBMeta")
    if DBMeta.select().count() == 0:
        meta = DBMeta(version=LATEST_META_VERSION)
        meta.save()

    print("That's all for now.")


@manager.command
def add_testdata():
    'Populates tables with test data (debug only, never use on production)'
    create_user('admin', 'admin', admin=True)
    u1 = create_user('user', 'user')
    u2 = create_user('user2', 'user2')

    create_hotspot('u_hs1', 'uhs1', u1)
    create_hotspot('u_hs2', 'uhs2', u1)
    create_hotspot('u_hs3', 'uhs3', u1)
    create_hotspot('u_hs4', 'uhs4', u1)
    create_hotspot('u_hs5', 'uhs5', u1)

    create_hotspot('u2_hs1', 'u2hs1', u2)
    create_hotspot('u2_hs2', 'u2hs2', u2)


if __name__ == '__main__':
    manager.run()
