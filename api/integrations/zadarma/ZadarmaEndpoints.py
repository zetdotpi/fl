import falcon
from pprint import pprint
from models import HS_mac_phone_pair


class ZadarmaStart:
    def on_get(self, req, resp):
        print('[GET] ZadarmaEndpoint integration test')
        if 'zd_echo' in req.params:
            print('found za_echo, returning')
            resp.body = req.params['zd_echo']
            return

    def on_post(self, req, resp):
        print('[POST] ZadarmaEndpoint incoming call')
        pprint('Headers')
        pprint(req.headers)
        pprint('Params')
        pprint(req.params)

        phone = req.params.get('caller_id')
        print('Phone is ', phone)
        if phone is None:
            print('no caller_id in params')
        else:
            phone = phone[1:]

            q = HS_mac_phone_pair.update(validated=True).where(HS_mac_phone_pair.phone==phone, HS_mac_phone_pair.validated==False)

            affected_count = q.execute()
            if affected_count > 0:
                print('ZadarmaEndpoint -> validated {0} pairs'.format(affected_count))
            else:
                print('ZadarmaEndpoint -> no pairs were affected')

            resp.status = falcon.HTTP_OK
            resp.media = {
                'redirect': 'blacklist',
                'caller_name': None
            }
