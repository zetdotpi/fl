import requests
import json
import falcon

import config
from api.hooks import check_auth, require_role
from models import User, Hotspot


def get_sms_balance():
    if config.SMS_GATEWAY == 'prostorsms':
        cred = {
            'login': config.PROSTORSMS_LOGIN,
            'password': config.PROSTORSMS_PASSWORD
        }
        res = requests.post('http://api.prostor-sms.ru/messages/v2/balance.json', json=cred)

        return float(res.json()['balance'][0]['balance'])
    else:
        return None


@falcon.before(check_auth)
@falcon.before(require_role('admin'))
class SystemStatsResource:
    def on_get(self, req, resp):
        users_count = User.select(None).count()
        active_users_count = User.select(None).where(User.pwd_hash != 'prereg').count()

        hotspots_count = Hotspot.select(None).count()

        sms_balance = get_sms_balance()

        data = {
            'stats': {
                'users_count': users_count,
                'active_users_count': active_users_count,
                'hotspots_count': hotspots_count,

                'sms_balance': sms_balance
            }
        }

        resp.body = json.dumps(data)
