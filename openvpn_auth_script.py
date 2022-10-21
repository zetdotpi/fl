import os

try:
    os.chdir('/var/www/example_app')
except:
    print('Could not change working directory')

from models import VpnUser

username = os.environ.get('username', None)
password = os.environ.get('password', None)

print(username)
print(password)

if username is None or password is None:
    exit(1)

# get hotspot vpn login by username
try:
    u = VpnUser.get(VpnUser.username == username)
    if u.password == password:
        print('everything is fine')
        exit(0)
    else:
        exit(1)

except VpnUser.DoesNotExist:
    exit(1)
