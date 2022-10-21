# import requests
# import json
import falcon
# import config

from pprint import pprint


class AvisoEndpoint:
    def on_get(self, req, resp):
        pprint(req.__dict__)
        resp.status = falcon.HTTP_NOT_IMPLEMENTED

    def on_post(self, req, resp):
        print('AVISO')
        pprint(req.headers)
        pprint(req.params)
        pprint(req.__dict__)
        resp.status = falcon.HTTP_NOT_IMPLEMENTED
