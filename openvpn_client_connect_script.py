import os
import sys
import config

from models.utils import ip_from_integer

try:
    os.chdir('/var/www/example_app')
except:
    print('whoa!')

from models import VpnUser

username = os.environ.get('username', None)
filepath = sys.argv[1]

print(40 * '=')
print(username)
print(filepath)
print(40 * '-')

if username is None:
    exit(1)

# get hotspot vpn login by username
try:
    u = VpnUser.get(VpnUser.username == username)
    with open(filepath, 'w+') as f:
        f.write('ifconfig-push {0} {1}'.format(ip_from_integer(u.address), config.VPN_POOL_SUBNET))
    exit(0)


except VpnUser.DoesNotExist:
    exit(1)
