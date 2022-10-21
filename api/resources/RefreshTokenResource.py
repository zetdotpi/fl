from datetime import datetime, timedelta
import json
import falcon
import jwt

from api.hooks import check_auth
from api import JWT_SECRET


@falcon.before(check_auth)
class RefreshTokenResource:
    def on_get(self, req, resp):
        # runs only if authorization token is present
        # so that USER is in request context and token is valid and not expired
        user = req.context['user']
        print(req.headers)
        print(req.stream.read().decode('utf8'))

        current_time = datetime.utcnow()

        claims = {
            'exp': current_time + timedelta(days=1),
            'iat': current_time,
            'nbf': current_time,

            # optional claims
            'login': user.login,
            'role': user.role
        }

        res_data = {
            'token': jwt.encode(claims, JWT_SECRET, algorithm='HS256').decode('utf8')
        }

        resp.status = falcon.HTTP_200
        resp.body = json.dumps(res_data)
        # resp.status = falcon.HTTP_403
