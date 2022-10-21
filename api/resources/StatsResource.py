from datetime import date, datetime, timedelta
import json
import falcon
from peewee import fn

from dateutil import parser as dateparser

from api.hooks import check_auth
from models import Hotspot, ROLES

from pprint import pprint


@falcon.before(check_auth)
class StatsResource:
    def on_get(self, req, resp, identity):
        # TODO: debug calls, remove.
        print('request params')
        print('==============')
        pprint(req.params)

        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Cannot get stats. Hotspot {0} not found.'.format(identity))

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner:

            req_type = req.params['type'] if 'type' in req.params else None
            # get parameters
            start_date = dateparser.parse(req.params['start']) if 'start' in req.params else None
            end_date = dateparser.parse(req.params['end']) if 'end' in req.params else None
            if req_type == 'weekdays':
                pass
                # TODO: return weekdays stats
            else:
                stats = _get_stats(hotspot, start_date, end_date)
                resp.body = json.dumps({'stats': stats})

        else:
            raise falcon.HTTPUnauthorized('')

    def on_post(self, req, resp):
        resp.body = json.dumps({'err': 'NotImplemented'})


_loginstats_query_startdate_enddate = '''
select
    datetime::date,
    count(distinct(phone))
from loginrecord
where
    hotspot_id = %s
    and datetime::date >= %s
    and datetime::date <= %s
group by datetime::date
order by datetime::date asc;
'''

_loginstats_query_startdate = '''
select
    datetime::date,
    count(*)
from loginrecord
where
    hotspot_id = %s
    and datetime::date >= %s
group by datetime::date
order by datetime::date asc;
'''

_weekdays_stats_query = '''
SELECT
    SUM(sub.c),
    EXTRACT(dow FROM sub.d) AS day 
FROM
    ( 
    SELECT 
        COUNT(DISTINCT(phone)) AS c,
        datetime::date AS d 
    FROM loginrecord 
    WHERE hotspot_id = %s AND datetime::date > %s
    GROUP BY datetime::date
    ) AS sub 
GROUP BY day 
ORDER BY day ASC;
'''


def _get_stats(hotspot, start_date=None, end_date=None):
    from models import database, LoginRecord, SMSUsageStat
    if start_date is not None and end_date is not None:
        days = (end_date - start_date).days

        login_stats_cursor = database.execute_sql(_loginstats_query_startdate_enddate,
                                                  (str(hotspot.id),
                                                   start_date.date().isoformat(),
                                                   end_date.date().isoformat()))

        sms_stats = SMSUsageStat.select(
            fn.DATE(SMSUsageStat.date).alias('day'),
            SMSUsageStat.count)\
            .where(SMSUsageStat.hotspot == hotspot,
                   SMSUsageStat.date >= start_date,
                   SMSUsageStat.date <= end_date)\
            .order_by(fn.DATE(SMSUsageStat.date).asc())

    elif start_date is not None:
        days = (date.today() - start_date).days

        login_stats_cursor = database.execute_sql(_loginstats_query_startdate,
                                                  (str(hotspot.id),
                                                   start_date.date().isoformat()))

        sms_stats = SMSUsageStat.select(
            fn.DATE(SMSUsageStat.date).alias('day'),
            SMSUsageStat.count)\
            .where(SMSUsageStat.hotspot == hotspot,
                   SMSUsageStat.date >= start_date)\
            .order_by(fn.DATE(SMSUsageStat.date))\
            .asc()

    else:
        days = 7
        start_date = datetime.today() - timedelta(days=7)

        login_stats_cursor = database.execute_sql(_loginstats_query_startdate,
                                                  (str(hotspot.id),
                                                   start_date.date().isoformat()))

        sms_stats = SMSUsageStat.select(
            fn.DATE(SMSUsageStat.date).alias('day'),
            SMSUsageStat.count)\
            .where(SMSUsageStat.hotspot == hotspot,
                   SMSUsageStat.date >= start_date)\
            .order_by(fn.DATE(SMSUsageStat.date))\
            .asc()

    login_result = {}

    for row in login_stats_cursor:
        login_result[row[0]] = row[1]

    sms_result = {}

    for s in sms_stats:
        sms_result[s.day] = s.count

    for day in range(days):
        dt = start_date + timedelta(day)
        d = date(dt.year, dt.month, dt.day)

        if login_result.get(d) is None:
            login_result[d] = 0

        if sms_result.get(d) is None:
            sms_result[d] = 0

    chartData = {
        'labels': [key.isoformat() for key in sorted(login_result)],
        'label': 'logins count',
        'loginData': [login_result[key] for key in sorted(login_result)],
        'smsData': [sms_result[key] for key in sorted(sms_result)]
    }

    return chartData
