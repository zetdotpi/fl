import json
import falcon
from api.hooks import check_auth
from models import OrderItem, Product, Hotspot

PAGE_SIZE = 20


@falcon.before(check_auth)
class BasketResource:
    def on_get(self, req, resp):
        items = OrderItem.select().where(OrderItem.client == req.context['user'], OrderItem.order.is_null())
        data = {
            'items': [item.as_dict() for item in items]
        }

        resp.body = json.dumps(data)

    def on_post(self, req, resp):
        print(req.media)

        data = req.media
        product_name = data['product_name']
        count = data['count']
        hotspot_identity = data['hotspot']

        product = Product.get(Product.name == product_name)
        hotspot = Hotspot.get(Hotspot.identity == hotspot_identity)

        oi = OrderItem(client=req.context['user'], item=product, count=count, hotspot=hotspot)
        oi.save()

        print('[OI] order item saved')

        items = OrderItem.select().where(OrderItem.client == req.context['user'], OrderItem.order.is_null())
        data = {
            'items': [item.as_dict() for item in items]
        }

        resp.body = json.dumps(data)
        # resp.body = json.dumps({'order_item': oi.as_dict()})

    def on_delete(self, req, resp):
        for order_item in req.context['user'].basket:
            order_item.delete_instance()

        resp.status = falcon.HTTP_OK
