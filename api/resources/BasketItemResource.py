import json
import falcon
from api.hooks import check_auth
from models import OrderItem


@falcon.before(check_auth)
class BasketItemResource:
    def on_put(self, req, resp, item_id):
        oi = OrderItem.get(OrderItem.id == item_id)
        if oi.client != req.context['user']:
            raise falcon.HTTPUnauthorized()

        data = json.load(req.stream)

        try:
            new_amount = data['amount']
            oi.amount = new_amount
            oi.save()
            resp.status = falcon.HTTP_OK

        except ValueError:
            raise falcon.HTTPBadRequest('amount should be an integer number')

        # client should reload basket now

    def on_delete(self, req, resp, item_id):
        oi = OrderItem.get(OrderItem.id == item_id)
        if oi.client != req.context['user']:
            raise falcon.HTTPUnauthorized()

        oi.delete_instance()
        resp.status = falcon.HTTP_OK
