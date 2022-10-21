import os
import json
import mimetypes
import falcon
from api.hooks import check_auth
from models import Hotspot, ROLES

# TODO: remove this shit. Import this from global settings
CLIENTS_UPLOAD_DIR = os.path.join(os.getcwd(), 'static', 'clients')


@falcon.before(check_auth)
class HotspotAppearanceImageResource:
    def on_post(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if not (ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner):
            raise falcon.HTTPUnauthorized('')

        ext = mimetypes.guess_extension(req.content_type)

        if ext in ['.png', '.jpg', '.jpeg', '.jpe']:
            target_folder = os.path.join(CLIENTS_UPLOAD_DIR, identity)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            img_filename = '{identity}{ext}'.format(identity=identity, ext=ext)
            img_path = os.path.join(target_folder, img_filename)

            with open(img_path, 'wb') as target_file:
                while True:
                    chunk = req.stream.read()
                    if not chunk:
                        break

                    target_file.write(chunk)

            hotspot.appearance.logo_image_filename = img_filename
            hotspot.appearance.save()
            resp.status = falcon.HTTP_CREATED

            logo_absolute_path = hotspot.appearance.as_dict()['logo_absolute_path']
            resp.location = logo_absolute_path
            resp.body = json.dumps({'logo_absolute_path': logo_absolute_path})
        else:
            raise falcon.HTTPUnsupportedMediaType('Image (jpg, png) required')

    def on_delete(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if not (ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner):
            raise falcon.HTTPUnauthorized('')

        if hotspot.appearance.logo_image_filename is not None:
            target_folder = os.path.join(CLIENTS_UPLOAD_DIR, identity)
            img_path = os.path.join(target_folder, hotspot.appearance.logo_image_filename)
            os.remove(img_path)

            hotspot.appearance.logo_image_filename = None
            hotspot.appearance.save()

            resp.status = falcon.HTTP_OK
        else:
            resp.status = falcon.HTTP_NOT_FOUND
