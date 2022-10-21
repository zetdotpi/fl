import falcon
import jwt
from models import User, ROLES
from api import JWT_SECRET


# AUTH HANDLER FOR RESOURCES
def check_auth(req, resp, resource, params):
    # def hook():
    if 'AUTHORIZATION' not in req.headers:
        print('No Authorization header found')
        raise falcon.HTTPUnauthorized(
            'Not found Authorized header',
            'Authorized header must be present and should contain JWT access token'
        )

    token = req.headers['AUTHORIZATION'][4:]
    try:
        claims = jwt.decode(token, JWT_SECRET)
        print(claims)
        user = User.get(User.login == claims['login'])
        req.context['user'] = user
    except User.DoesNotExist:
        raise falcon.HTTPUnauthorized(
            'User does not exist',
            'Please use existing login'
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise falcon.HTTPUnauthorized(
            'Token expired',
            'Please login or refresh token'
        )


def require_role(role):
    def hook(req, resp, resource, params):
        # reject if role is lower in hierarchy
        if req.context['user'].role is None or ROLES[req.context['user'].role] < ROLES[role]:
            raise falcon.HTTPUnauthorized()

    return hook
