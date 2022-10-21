JWT_SECRET = 'KJNPIuhv932v0iuvrfpiu wh_W( BirnbH)hu23-98vu-928q4vuQIPU#RHWOIU%$W 5sdfw23Bq$'

import falcon

from config import CLIENTS_STATIC_PATH

from api.middleware import CorsMiddleware
from api.resources import AuthResource, CurrentUserProfileResource, RefreshTokenResource, \
    RegistrationResource, RegistrationProfileResource, \
    HotspotsResource, HotspotResource, HotspotAppearanceResource, \
    HotspotAppearanceImageResource, HotspotOverviewResource, \
    SetupHotspotConnectionResource, SetupHotspotResource, \
    TargetingExportResource, \
    UsersResource, UserResource, StatsResource, SystemStatsResource, \
    BasketResource, BasketItemResource, \
    OrdersResource, OrderResource, OrderItemResource, OrderActionResource
from api.integrations import zadarma, instagram

# create and setup API
app = falcon.API(middleware=[CorsMiddleware()])

app.req_options.auto_parse_form_urlencoded = True

app.add_route('/auth', AuthResource())
app.add_route('/auth/user', CurrentUserProfileResource())
app.add_route('/auth/refresh', RefreshTokenResource())

app.add_route('/auth/register', RegistrationResource())
app.add_route('/auth/register/profile', RegistrationProfileResource())

# post to HotspotsResource for registration of new resource
app.add_route('/hs', HotspotsResource())
app.add_route('/hs/{identity}', HotspotResource())
app.add_route('/hs/{identity}/overview', HotspotOverviewResource())

# TODO: add this routes implementation
app.add_route('/hs/{identity}/connect', SetupHotspotConnectionResource())
app.add_route('/hs/{identity}/configure', SetupHotspotResource())

app.add_route('/hs/{identity}/appearance', HotspotAppearanceResource())
app.add_route('/hs/{identity}/logo', HotspotAppearanceImageResource())

app.add_route('/hs/{identity}/stats', StatsResource())

# hotspots extended functions
app.add_route('/hs/{identity}/targeting', TargetingExportResource())

app.add_route('/users', UsersResource())
app.add_route('/users/{login}', UserResource())

app.add_route('/basket', BasketResource())
app.add_route('/basket/{item_id}', BasketItemResource())

app.add_route('/orders', OrdersResource())
app.add_route('/orders/{order_id}', OrderResource())
app.add_route('/orders/{order_id}/{item_id}', OrderItemResource())
app.add_route('/orders/{order_id}/action', OrderActionResource())

app.add_route('/stats', SystemStatsResource())

print(CLIENTS_STATIC_PATH)
# app.add_static_route('/docs', CLIENTS_STATIC_PATH)

# Yandex.Kassa integration

# app.add_route('/integrations/yandex_kassa/check', yandex_kassa.CheckOrderEndpoint())
# app.add_route('/integrations/yandex_kassa/aviso', yandex_kassa.AvisoEndpoint())

# Zadarma integration
app.add_route('/integrations/zadarma/start', zadarma.ZadarmaStart())

# Instagram oauth integration
app.add_route('/integrations/instagram', instagram.InstagramLogin())


if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
