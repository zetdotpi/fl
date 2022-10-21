import json
import falcon
from api.hooks import check_auth
import rosapi
import config
from models import Hotspot, ROLES
from routerboard import RB


# SETUP CONECTION TO ROUTER
@falcon.before(check_auth)
class SetupHotspotConnectionResource:
    def on_post(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] < ROLES['admin'] and req.context['user'] != hotspot.owner:
            raise falcon.HTTPUnauthorized('')

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Bad request', 'Request without body')

        data = json.loads(body.decode('utf8'))

        username = data['username']
        password = data['password']

        try:
            print('Connecting to client router with VPN')
            rb = RB.connect(hotspot.vpn_user.get_ip_string(), username, password, 8728)
            print('Okay!')
            print('Performing cleanup users and groups')
            rb.cleanup_users_and_groups(config.API_GROUP_NAME, config.API_USER_NAME)

            print('Adding Example group')
            rb.add_group(config.API_GROUP_NAME, config.API_GROUP_PERMISSIONS)
            print('Done')
            print('Adding Example user')
            rb.add_user(config.API_USER_NAME, config.API_USER_PASSWORD, config.API_GROUP_NAME, config.VPN_NET)
            print('Done. Redirecting to interfaces setup')
            resp.status = falcon.HTTP_OK
        except rosapi.RosAPIConnectionError:
            print('rosapi.RosAPIConnectionError')
            print('Cannot connect to client router with VPN!')
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = json.dumps({'error': 'Cannot connect to router'})
        except rosapi.RosAPIError as e:
            print('rosapi.RosAPIError!')
            errmsg = e.value[b'message'].decode('ascii')
            print(errmsg)
            resp.body = json.dumps({'error': errmsg})
        else:
            print('Else after two excepts. Whoa!')
