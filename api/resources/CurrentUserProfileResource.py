import json
import falcon

from api.hooks import check_auth


@falcon.before(check_auth)
class CurrentUserProfileResource:
    def on_get(self, req, resp):
        user = req.context['user']
        resp.body = json.dumps({'data': user.as_dict()})
