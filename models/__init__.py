import platform
from peewee import *
import config

DB_NAME = 'test.db'

if config.DEBUG is True:
    print('DEBUG mode ON')
if config.DEBUG is True and platform.node() != 'Example-f21':
    database = PostgresqlDatabase(
        config.DB_NAME,
        host=config.DB_HOST,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD
    )
else:
    print('Using Postgres')
    database = PostgresqlDatabase(
        config.DB_NAME,
        host=config.DB_HOST,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD
    )

SOCIAL_NETWORKS = (
    ('vk', 'vkontakte'),
    ('ok', 'odnoklassniki'),
    ('fb', 'facebook'),
    ('tw', 'twitter')
)

from .BaseModel import BaseModel
from .DBMeta import DBMeta
from .Balance import Balance
from .OrganisationInfo import OrganisationInfo
from .Client import Client
from .User import User
from .Appearance import Appearance
from .VpnUser import VpnUser
from .Hotspot import Hotspot
from .HotspotUser import HotspotUser
from .SocialDetails import SocialDetails
from .LoginRecord import LoginRecord
from .PublicationImage import PublicationImage
from .VKPublication import VKPublication
from .FacebookPublication import FacebookPublication
from .OKPublication import OKPublication
from .TwitterPublication import TwitterPublication
from .GooglePlusPublication import GooglePlusPublication
from .RegistrationToken import RegistrationToken
from .SMSLoginToken import SMSLoginToken
from .HS_mac_phone_pair import HS_mac_phone_pair
from .HS_Phone import HS_Phone
from .HS_Device import HS_Device
from .HS_Pin import HS_Pin
# from .HS_AuthRecord import HS_AuthRecord
from .SMSUsageStat import SMSUsageStat
from .roles import ROLES
from .Order import Order
from .Product import Product
from .OrderItem import OrderItem
