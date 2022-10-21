import json
import falcon
from api.hooks import check_auth
from models import Order, ROLES


@falcon.before(check_auth)
class OrderResource:
    def on_get(self, req, resp, order_id):
        try:
            order = Order.get(Order.id == order_id)
        except Order.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(order_id), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == order.client:
            resp.body = json.dumps({'order': order.as_dict()})

        else:
            raise falcon.HTTPUnauthorized('')

    def on_post(self, req, resp):
        resp.body = json.dumps({'err': 'NotImplemented'})
