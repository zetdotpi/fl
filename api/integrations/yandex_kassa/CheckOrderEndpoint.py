from datetime import datetime, timezone
from pprint import pprint

# import requests
# import json
import falcon
# import config

RESP_BODY_SUCCESS = '''
<checkOrderResponse
    performedDatetime="{performed_datetime}"
    code="{code}"
    invoiceId="{invoice_id}"
    shopId="{shop_id}"/>'''


class CheckOrderEndpoint:
    def on_get(self, req, resp):
        pprint(req.__dict__)
        resp.status = falcon.HTTP_NOT_IMPLEMENTED

    def on_post(self, req, resp):
        pprint(req.headers)
        pprint(req.params)
        pprint(req.__dict__)

        shop_id = req.get_param('shopId')
        invoice_id = req.get_param('invoiceId')
        code = '0'
        performed_datetime = datetime.now(timezone.utc).astimezone().isoformat()

        resp.body = RESP_BODY_SUCCESS.format(performed_datetime=performed_datetime,
                                             code=code,
                                             invoice_id=invoice_id,
                                             shop_id=shop_id)
        pprint(resp.body)
