import os
import paramiko
import config


def send_command(router, command):
    key = paramiko.DSSKey.from_private_key(open(config['KEY_PATH']))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=router.vpn_user.get_ip_string(), port=router.port or 22022, username='Example', pkey=key)
    client.exec_command(command)
    client.close()


def add_hotspot_user(router, user):
    from pprint import pprint
    pprint(router.__dict__)
    pprint(user.__dict__)
    cmd = 'ip hotspot user add name="{0}" password="{1}"'.format(user.login, user.password)
    send_command(router, cmd)


def remove_hotspot_user(router, user):
    cmd = 'ip hotspot user remove numbers="{0}"'.format(user.login)
    send_command(router, cmd)


def flash_dir_is_available(router):
    t = paramiko.Transport((router.vpn_user.get_ip_string(), 22022))
    t.connect(username=config['API_USER_NAME'], password=config['API_USER_PASSWORD'])
    sftp = paramiko.SFTPClient.from_transport(t)
    available = 'flash' in sftp.listdir()
    sftp.close()
    t.close()
    return available


def upload_file(router, src, dst):
    t = paramiko.Transport((router.vpn_user.get_ip_string(), 22022))
    t.connect(username=config['API_USER_NAME'], password=config['API_USER_PASSWORD'])
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(src, dst)
    sftp.close()
    t.close()


def upload_folder(router, src, dst):
    t = paramiko.Transport((router.vpn_user.get_ip_string(), 22022))
    t.connect(username=config['API_USER_NAME'], password=config['API_USER_PASSWORD'])
    sftp = paramiko.SFTPClient.from_transport(t)
    os.chdir(os.path.split(src)[0])
    parent = os.path.split(src)[1]
    for walker in os.walk(parent):
        try:
            sftp.mkdir(os.path.join(dst, walker[0]))
        except:
            pass
        for file in walker[2]:
            sftp.put(os.path.join(walker[0], file), os.path.join(dst, walker[0], file))
    sftp.close()
    t.close()
