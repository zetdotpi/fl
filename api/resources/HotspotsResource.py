import math
import json
from datetime import date, timedelta
import uuid
import falcon
from unidecode import unidecode
from api.hooks import check_auth
from models import Hotspot, Appearance, VpnUser, ROLES
from models.utils import generate_token

from datetime import datetime

PAGE_SIZE = 20


@falcon.before(check_auth)
class HotspotsResource:
    def on_get(self, req, resp):
        print('!!!!!!!!!!!!!!', datetime.now())
        if ROLES[req.context['user'].role] >= ROLES['admin']:
            hotspots = Hotspot.select()
        else:
            hotspots = Hotspot.select().where(Hotspot.owner == req.context['user'])

        total_count = str(hotspots.count())
        max_page = math.ceil(hotspots.count() / PAGE_SIZE)
        if 'page' in req.params:
            page = req.get_param_as_int('page')
            if not(0 < page <= max_page):
                raise falcon.HTTPNotFound()
            else:
                hotspots = hotspots.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)

        data = {
            'hotspots': [hs.as_dict() for hs in hotspots.order_by(Hotspot.name)],
            'pages': max_page
        }

        resp.body = json.dumps(data)
        resp.set_header('X-Total-Count', total_count)
        print('!!!!!!!!!!!!!!', datetime.now())

    def on_post(self, req, resp):
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Bad request', 'Request without body')

        data = json.loads(body.decode('utf8'))
        name = data['name']

        ovpn_identity = uuid.uuid4().hex
        ovpn_password = generate_token(length=8)

        vpn_user = VpnUser(username=ovpn_identity, password=ovpn_password)
        vpn_user.address = VpnUser.get_new_ip()
        vpn_user.save()

        appearance = Appearance()
        appearance.save()

        user = req.context['user']

        paid_until = date.today() if user.hotspots.count() > 0 else date.today() + timedelta(days=5)

        hotspot = Hotspot(
            name=name,
            identity=name,
            owner=user.id,
            appearance=appearance,
            vpn_user=vpn_user,
            paid_until=paid_until)
        hotspot.save()

        transliterated_name = unidecode(hotspot.name.replace(' ', '_'))

        hotspot.identity = '{0}_{1}_{2}'.format(user.id, transliterated_name, hotspot.id)
        print(hotspot.identity)
        hotspot.save()

        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({'hotspot': hotspot.as_dict()})
