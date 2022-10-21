from datetime import datetime, timedelta
import json
import falcon
import jwt

from models import User
from api import JWT_SECRET


class AuthResource:
    def on_post(self, req, resp):
        body = req.stream.read()
        if body:
            credentials = json.loads(body.decode('utf8'))

            if not all(item in credentials for item in ('username', 'password')):
                raise falcon.HTTPBadRequest('Credentials missing', 'Please provide username and password')

            username = credentials['username']
            password = credentials['password']

            try:
                u = User.get(User.login == username)

                if u.check_password(password) is False:
                    raise falcon.HTTPUnauthorized('Authentication failed', 'Wrong username or password')

                current_time = datetime.utcnow()

                claims = {
                    'exp': current_time + timedelta(days=1),
                    'iat': current_time,
                    'nbf': current_time,

                    # optional claims
                    'login': u.login,
                    'role': u.role
                }

                res_data = {
                    'token': jwt.encode(claims, JWT_SECRET, algorithm='HS256').decode('utf8')
                }

                resp.status = falcon.HTTP_200
                resp.body = json.dumps(res_data)

            except User.DoesNotExist:
                raise falcon.HTTPUnauthorized('Authentication failed', 'Wrong username or password')

        else:
            resp.status = falcon.HTTP_400
