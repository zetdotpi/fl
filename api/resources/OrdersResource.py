import json
import falcon
from api.hooks import check_auth
from models import Order, OrderItem, ROLES

PAGE_SIZE = 20


@falcon.before(check_auth)
class OrdersResource:
    def on_get(self, req, resp):
        if ROLES[req.context['user'].role] >= ROLES['admin']:
            orders = Order.select()
        else:
            orders = Order.select().where(Order.client == req.context['user'])

        data = {
            'orders': [order.as_dict() for order in orders]
        }

        resp.body = json.dumps(data)
        # resp.set_header('X-Total-Count', total_count)

    def on_post(self, req, resp):
        items = OrderItem.select().where(
            OrderItem.client == req.context['user'],
            OrderItem.order.is_null())
        order = Order(client=req.context['user'])
        order.save()

        for item in items:
            item.order = order
            item.save()

        order.generate_invoice_pdf()

        resp.status = falcon.HTTP_CREATED
        resp.body = json.dumps({'order': order.as_dict()})
