import io
import csv
# import json
import hashlib
import falcon
from api.hooks import check_auth
from peewee import fn
from models import Hotspot, LoginRecord, ROLES


# @falcon.before(check_auth)
class TargetingExportResource:
    def on_get(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        # if not (ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner):
        #     raise falcon.HTTPUnauthorized('')

        memfile = io.StringIO()
        writer = csv.writer(memfile, delimiter=',')

        export_type = req.params['type']
        if export_type == 'yandex':
            generate_for_yandex(hotspot, writer)
            resp.downloadable_as = 'yandex_export.csv'

        elif export_type == 'adwords':
            generate_for_google(hotspot, writer)
            resp.downloadable_as = 'adwords_export.csv'

        elif export_type == 'vk':
            generate_for_vk(hotspot, writer)
            resp.downloadable_as = 'vk_export.csv'

        elif export_type == 'facebook':
            generate_for_fb(hotspot, writer)
            resp.downloadable_as = 'fb_export.csv'

        else:
            raise falcon.HTTPBadRequest('no export_type param')

        # dumping response
        memfile.seek(0)
        resp.body = memfile.read()


def generate_for_yandex(hotspot, writer):
    data = hotspot.logins_log.select((fn.MD5(LoginRecord.phone)).alias('phone')).distinct()
    writer.writerow(['phone'])
    for element in data:
        writer.writerow([hashlib.md5(element.phone.encode('utf8')).hexdigest()])


def generate_for_google(hotspot, writer):
    data = hotspot.logins_log.select(LoginRecord.phone.alias('phone')).distinct()
    writer.writerow(['Phone'])
    for element in data:
        writer.writerow([hashlib.sha256(element.phone.encode('utf8')).hexdigest()])


def generate_for_vk(hotspot, writer):
    data = hotspot.logins_log.select((fn.MD5(LoginRecord.phone)).alias('phone')).distinct()
    writer.writerow(['phone'])
    for element in data:
        writer.writerow([hashlib.md5(element.phone.encode('utf8')).hexdigest()])


def generate_for_fb(hotspot, writer):
    data = hotspot.logins_log.select(LoginRecord.phone.alias('phone')).distinct()
    writer.writerow(['phone'])
    for element in data:
        writer.writerow([hashlib.sha256(element.phone.encode('utf8')).hexdigest()])
