import json
import falcon
from api.hooks import check_auth
from models import Hotspot, ROLES


@falcon.before(check_auth)
class HotspotAppearanceResource:
    def on_get(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner:
            resp.body = json.dumps({'appearance': hotspot.appearance.as_dict()})

        else:
            raise falcon.HTTPUnauthorized('')

    def on_put(self, req, resp, identity):
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Bad request', 'Request without body')

        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if not (ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner):
            raise falcon.HTTPUnauthorized('')

        data = json.loads(body.decode('utf8'))
        print(data)
        title = data['title']
        text = data['text']

        appearance = hotspot.appearance
        appearance.title = title
        appearance.text = text
        appearance.save()
        resp.body = json.dumps({'appearance': hotspot.appearance.as_dict()})
    # def on_post(self, req, resp):
    #     resp.body = json.dumps({'err': 'NotImplemented'})
