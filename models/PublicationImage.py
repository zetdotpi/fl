import vk
from peewee import *
from . import BaseModel, Hotspot, config


class PublicationImage(BaseModel):
    class Meta:
        order_by = ('-id',)

    hotspot = ForeignKeyField(Hotspot, backref='publication_images')
    direct_link = TextField()
    vk_image_id = CharField()

    @classmethod
    def upload(cls, hotspot, image_file):
        api = vk.API(access_token=config.VK_ACCESS_TOKEN)
        upload_data = api.photos.getUploadServer(group_id=config.VK_GROUP_ID, album_id=config.VK_ALBUM_ID)

        tmpdir = os.path.join(tempfile.gettempdir(), 'Example', hotspot.identity)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)

        safe_filename = secure_filename(image_file.filename)

        tmpfile_path = os.path.join(tmpdir, safe_filename)
        tmpfile = open(tmpfile_path, 'wb')
        tmpfile.write(image_file.read())
        tmpfile.flush()
        tmpfile.close()
        tmpfile = open(tmpfile_path, 'rb')

        files = {'photo': tmpfile}
        upload_resp = requests.post(upload_data['upload_url'], files=files)

        if upload_resp.ok:
            os.remove(tmpfile_path)
            resp_json = json.loads(upload_resp.text)

            # DEBUG
            # from pprint import pprint
            # pprint(resp_json)

            image_data = api.photos.save(group_id=config.VK_GROUP_ID,
                                         album_id=config.VK_ALBUM_ID,
                                         server=resp_json['server'],
                                         photos_list=resp_json['photos_list'],
                                         hash=resp_json['hash'])[0]

            # pprint(image_data)

            # album_id = image_data['album_id']
            image_id = image_data['id']
            # getting maximum photo size
            photo_sizes = {int(k[6:]): v for k, v in image_data.items() if k.startswith('photo')}
            image_url = photo_sizes[max(photo_sizes)]
            # pprint(max(photo_sizes))
            # pprint(image_url)
            # vk_image_path = 'https://vk.com/photo-{0}_{1}'.format(config.VK_GROUP_ID, image_id)

            pub_img = cls(hotspot=hotspot, direct_link=image_url, vk_image_id=image_id)
            pub_img.save()
            return pub_img

        os.remove(tmpfile_path)
        raise Exception('cannot upload file')

    def vk_path(self):
        return 'https://vk.com/photo-{0}_{1}'.format(config.VK_GROUP_ID, self.vk_image_id)

    def vk_id(self):
        return 'photo-{0}_{1}'.format(config.VK_GROUP_ID, self.vk_image_id)
