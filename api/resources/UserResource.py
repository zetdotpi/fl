import json
import falcon
from api.hooks import check_auth, require_role
from models import User


@falcon.before(check_auth)
@falcon.before(require_role('admin'))
class UserResource:
    def on_get(self, req, resp, login):
        try:
            user = User.get(User.login == login)
            resp.body = json.dumps({'user': user.as_dict()})
        except User.DoesNotExist:
            raise falcon.HTTPNotFound('User {0} not found'.format(login), 'please provice correct user login')

    def on_put(self, req, resp, login):
        try:
            user = User.get(User.login == login)

        except User.DoesNotExist:
            raise falcon.HTTPNotFound('User {0} not found'.format(login), 'please provice correct user login')

        if req.context['user'].role == 'admin' or req.context['user'].login == user.login:
            data = req.media
            from pprint import pprint
            pprint(data)
            # email = data.profile.email
            name = data['profile']['name']
            phone = data['profile']['phone']

            org_address = data['organisationInfo']['address']
            org_inn = data['organisationInfo']['inn']
            org_kpp = data['organisationInfo']['kpp']
            org_name = data['organisationInfo']['name']
            org_phone = data['organisationInfo']['phone']

            cp = user.client_profile
            # cp.contact_email = email
            cp.contact_name = name
            cp.contact_phone = phone
            cp.save()

            oi = user.organisation_info
            oi.address = org_address
            oi.inn = org_inn
            oi.kpp = org_kpp
            oi.name = org_name
            oi.phone = org_phone
            oi.save()

            resp.media = {'user': user.as_dict()}
        else:
            raise falcon.HTTPUnauthorized('you are not allowed to do this')
