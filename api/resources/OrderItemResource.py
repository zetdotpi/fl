import json
import falcon
from api.hooks import check_auth
from models import OrderItem, ROLES


@falcon.before(check_auth)
class OrderItemResource:
    def on_delete(self, req, resp, order_id, item_id):
        item = OrderItem.get(OrderItem.id == item_id)
        if ROLES[req.context['user'].role] < ROLES['admin'] and item.order.client != req.context['user']:
            raise falcon.HTTPUnauthorized('')
        else:
            item.delete_instance()
            resp.status = falcon.HTTP_OK

    def on_put(self, req, resp, order_id, item_id):
        # REQUEST JSON OBJECT SHOULD CONTAIN AMOUNT FIELD
        item = OrderItem.get(OrderItem.id == item_id)
        if ROLES[req.context['user'].role] < ROLES['admin'] and item.order.client != req.context['user']:
            raise falcon.HTTPUnauthorized('')

        data = json.load(req.stream)
        amount = data['amount']

        if amount <= 0:
            amount = 1

        item.count = amount
        item.save()

        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({'item': item.as_dict()})
