import falcon
import json
from models import database, RegistrationToken


class RegistrationProfileResource:
    def on_post(self, req, resp):
        body = req.stream.read()
        data = json.loads(body.decode('utf8'))

        token_str = data.get('regToken')
        if token_str is None:
            raise falcon.HTTPNotFound('Invalid registration token')

        token = RegistrationToken.get(RegistrationToken.value == token_str)
        if token is None or not token.valid:
            raise falcon.HTTPNotFound('Token not found or invalid')

        user = token.user
        org_info = user.organisation_info
        client_profile = user.client_profile

        with database.atomic() as transaction:
            try:
                orgInfo = data.get('organisationInfo')
                if orgInfo is not None:
                    org_info.name = orgInfo.get('name')
                    org_info.inn = orgInfo.get('inn')
                    org_info.kpp = orgInfo.get('kpp')
                    org_info.address = orgInfo.get('address')
                    org_info.phone = orgInfo.get('phone')

                client_profile.contact_name = data['profile']['name']
                client_profile.contact_phone = data['profile']['phone']

                client_profile.save()
                org_info.save()

                user.set_password(data.get('password'))
                user.save()

            except Exception as e:
                transaction.rollback()
                print('DB error')
                print(e.with_traceback(None))
                raise falcon.HTTPInternalServerError('DB error.')
