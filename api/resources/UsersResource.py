import math
import json
import falcon
from api.hooks import check_auth, require_role
from models import User, Client

PAGE_SIZE = 50


@falcon.before(check_auth)
@falcon.before(require_role('admin'))
class UsersResource:
    def on_get(self, req, resp):

        max_page = math.ceil(User.select(None).count() / PAGE_SIZE)
        if 'page' in req.params:
            page = req.get_param_as_int('page')
            if not(0 < page <= max_page):
                raise falcon.HTTPNotFound()
            else:
                print('pagination')
                users = User.select().offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)
                print(len(users))
        else:
            users = User.select()
            print(len(users))

        total_users_count = str(User.select(None).count())
        resp.set_header('X-Total-Count', total_users_count)

        resp.body = json.dumps(
            {
                'users': [user.as_dict() for user in users],
                'pages': max_page
            }
        )

    def on_post(self, req, resp):
        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Wrong/incomplete data.', 'Please provide complete data.')

        data = json.loads(body.decode('utf8'))
        user_data = data['user']

        client_profile = Client(
            contact_email=user_data['email'],
            contact_name=user_data['profile']['name'],
            contact_phone=user_data['profile']['phone'])
        client_profile.save()

        user = User(
            login=user_data['email'],
            client_profile=client_profile
        )

        user.set_password(user_data['password'])
        user.save()

        resp.status = falcon.HTTP_CREATED
        resp.body = json.dumps({'user': user.as_dict()})
