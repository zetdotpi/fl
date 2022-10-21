import json
from datetime import date, timedelta
import falcon
from peewee import fn, SQL
from api.hooks import check_auth
from models import LoginRecord, Hotspot, ROLES

DEFAULT_PERIOD = 90  # measured in days


def get_browser_stats(hotspot):
    start_date = date.today() - timedelta(days=DEFAULT_PERIOD)

    stats = LoginRecord.select(fn.COUNT(LoginRecord.id).alias('count'), LoginRecord.ua_browser)\
        .where(LoginRecord.hotspot == hotspot, LoginRecord.datetime >= start_date)\
        .group_by(LoginRecord.ua_browser)\
        .order_by(SQL('count DESC'))

    res = [(line.ua_browser, line.count) for line in stats]
    return res


def get_platform_stats(hotspot):
    start_date = date.today() - timedelta(days=DEFAULT_PERIOD)

    stats = LoginRecord.select(fn.COUNT(LoginRecord.id).alias('count'), LoginRecord.ua_platform)\
        .where(LoginRecord.hotspot == hotspot, LoginRecord.datetime >= start_date)\
        .group_by(LoginRecord.ua_platform)\
        .order_by(SQL('count DESC'))

    res = [(line.ua_platform, line.count) for line in stats]
    return res


@falcon.before(check_auth)
class HotspotOverviewResource:
    def on_get(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner:
            bs = get_browser_stats(hotspot)
            ps = get_platform_stats(hotspot)
            resp.media = {
                'browsers': {
                    'labels': [line[0] if line[0] != None else 'unknown' for line in bs],
                    'label': 'browsers stats',
                    'data': [line[1] for line in bs]
                },
                'platforms': {
                    'labels': [line[0] if line[0] != None else 'unknown' for line in ps],
                    'label': 'platforms stats',
                    'data': [line[1] for line in ps]
                }
            }

        else:
            raise falcon.HTTPUnauthorized('')
