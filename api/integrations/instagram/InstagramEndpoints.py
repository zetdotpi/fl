import json
import requests
import falcon
import config
from pprint import pprint
# from models import HS_mac_phone_pair


class InstagramLogin:
    def on_get(self, req, resp):
        print('[IG LOGIN] GET')
        print(req.params)
        if 'error' in req.params:
            print('got error')
            pprint(req.params)
            raise falcon.HTTPBadRequest('error', 'error is present')
        elif 'code' in req.params:
            request_token(req.params['code'], req.params['state'])


def request_token(code, state):
    res = requests.post(
        'https://api.instagram.com/oauth/access_token',
        data={
            'client_id': config.IG_CLIENT_ID,
            'client_secret': config.IG_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://api.example.com/integrations/instagram?state={}'.format(state),
            'code': code

        }
    )
    print(res.url)
    print(res.status_code)

    if res.status_code == requests.codes.ok:
        pprint(res.json())
    else:
        print('something went wrong while requesting ig authorization')
        print(res)
