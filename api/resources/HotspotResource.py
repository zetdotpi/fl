import json
import falcon
from api.hooks import check_auth
from models import Hotspot, ROLES


@falcon.before(check_auth)
class HotspotResource:
    def on_get(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner:
            resp.body = json.dumps({'hotspot': hotspot.as_dict()})

        else:
            raise falcon.HTTPUnauthorized('')

    def on_post(self, req, resp):
        resp.body = json.dumps({'err': 'NotImplemented'})
