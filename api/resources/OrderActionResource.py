import falcon
from api.hooks import check_auth, require_role
from models import Order
from datetime import date, timedelta

DEFINED_ACTIONS = ['confirm_payment']


@falcon.before(check_auth)
@falcon.before(require_role('admin'))
class OrderActionResource:
    def on_post(self, req, resp, order_id):
        '''
        request.media should be == {
            'action': 'ACTION_NAME',
            'params': {
                'param1': 'value1',
                ...,
                'paramN': 'valueN'
            }
        }

        'params' can be None or can be undefined
        '''
        print(req.media)
        action = req.media.get('action')
        if action not in DEFINED_ACTIONS:
            raise falcon.HTTPBadRequest('wrong action name "{0}"'.format(action))
        try:
            order = Order.get(Order.id == order_id)
            _process_order_action(order, action)
            resp.status = falcon.HTTP_OK
        except Order.DoesNotExist:
            raise falcon.HTTPNotFound('order with id {0} does not exist'.format(order_id))


def _process_order_action(order, action):
    if action == 'confirm_payment':
        _action_complete_order(order)


def _action_complete_order(order):
    # deliver items and mark order as completed
    for oi in order.items:
        if oi.item.name == 'hotspotService_monthly':
            hs = oi.hotspot
            if hs.paid_until is None or hs.paid_until <= date.today():
                hs.paid_until = date.today() + timedelta(days=30 * oi.count)
            else:
                hs.paid_until = hs.paid_until + timedelta(days=30 * oi.count)
            hs.save()
        else:
            print('unknown product name == {}'.format(oi.item.name))
    order.paid = True
    order.enrolled = True
    order.save()
