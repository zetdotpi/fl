import os
import time
import json
import falcon
from api.hooks import check_auth
from models import Hotspot, ROLES
from routerboard import RB, RouterboardUploader
import config


# SETUP HOTSPOT BRIDGE, etc
@falcon.before(check_auth)
class SetupHotspotResource:
    def on_get(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] >= ROLES['admin'] or req.context['user'] == hotspot.owner:
            rb = RB.connect(hotspot.vpn_user.get_ip_string(), config.API_USER_NAME, config.API_USER_PASSWORD)
            interfaces = rb.list_interfaces()
            # ifnames = rb.get_interface_names()
            resp.status = falcon.HTTP_OK
            resp.body = json.dumps(interfaces)

        else:
            raise falcon.HTTPUnauthorized('')

    def on_post(self, req, resp, identity):
        try:
            hotspot = Hotspot.get(Hotspot.identity == identity)
        except Hotspot.DoesNotExist:
            raise falcon.HTTPNotFound('Hotspot {0} not found'.format(identity), 'please provice correct hotspot id')

        if ROLES[req.context['user'].role] < ROLES['admin'] and req.context['user'] != hotspot.owner:
            raise falcon.HTTPUnauthorized('')

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Bad request', 'Request without body')
        # TODO: read hotspot interfaces enumeration from request body
        # configure hotspot bridge, add interfaces (add virtual ap if required)
        # return updated object:
        req_data = json.loads(body.decode('utf8'))
        ifnames = req_data['ifnames']
        # if len(ifnames) == 0:
        #     flash('Должен быть отмечен хотя бы один интерфейс.')
        # else:

        rb = RB.connect(
            hotspot.vpn_user.get_ip_string(),
            config.API_USER_NAME,
            config.API_USER_PASSWORD,
            hotspot.port or 8728)
        print('Performing pre-setup cleanup')
        rb.cleanup()

        print('Enabling ssh for {0}'.format(hotspot.owner.login))
        rb.enable_ssh()

        print('Getting software version')
        version = rb.get_version()
        print(version)

        print('Setting up hotspot for {0}'.format(hotspot.owner.login))

        uploader = RouterboardUploader(hotspot)
        uploader.connect()

        use_flash_dir = uploader.flash_dir_is_available()
        if use_flash_dir:
            mikrotik_upload_dir = '/flash/'
        else:
            mikrotik_upload_dir = '/'

        # Uploading captive portal pages
        uploader.upload_folder(
            os.path.join(config.MIKROTIK_FILES_PATH, 'Example_hotspot'),
            mikrotik_upload_dir
        )
        uploader.close()

        # defining configuration names
        pool_name = 'ExamplePOOL'
        pool_range = '10.100.0.100-10.100.255.254'
        rb.add_pool(pool_name, pool_range)
        print('Pool added.')

        security_profile_name = 'ExampleSP'
        rb.add_wireless_security_profile(name=security_profile_name, mode='none')
        print('Wireless security profile added.')

        # setting wlans secutiry profile to ExampleSP
        # creating virtualap is necessary
        wlans = rb._api.get_resource('/interface/wireless')
        for ifname in ifnames:
            if ifname in [wlan['name'] for wlan in wlans.get()]:
                wlan = wlans.get(name=ifname)[0]
                wlans.set(id=wlan['id'], security_profile='ExampleSP', disabled='no')
            elif ifname == 'add_virtualAP':
                print('Adding virtualAP')
                wlan1 = rb._api.get_resource('/interface/wireless').get(default_name='wlan1')[0]
                wlans.add(
                    master_interface=wlan1['name'],
                    security_profile='ExampleSP',
                    ssid='Example',
                    name='ExampleAP',
                    disabled='no')
                ifnames.pop(ifnames.index('add_virtualAP'))
                ifnames.append('ExampleAP')
            else:
                pass
        print('Wireless interfaces security profiles set.')

        bridge_name = 'ExampleBR'
        bridge_address = '10.100.0.1/16'
        rb.add_bridge(bridge_name, ifnames)
        print('Bridge added.')
        rb.add_address(bridge_name, bridge_address)
        print('Address assigned.')

        # adding open security profile
        dhcp_network = '10.100.0.0/16'
        rb.add_dhcp_network(dhcp_network, bridge_address[:-3])
        print('DHCP network is set.')
        dhcp_name = 'ExampleDHCP'
        rb.add_dhcp_srv(dhcp_name, bridge_name, pool_name)
        print('DHCP server is up.')

        rb.enable_masquerade(dhcp_network)

        # hotspot server profile
        hs_user_profile_name = 'ExampleUSR'
        rb.add_hotspot_user_profile(
            name=hs_user_profile_name,
            keepalive_timeout='2h',
            shared_users='unlimited',
            status_autorefresh='2h'
        )
        print('Hotspot user profile is set.')

        # set ssl certificates
        hs_profile_name = 'ExampleHSProfile'
        # hs_html_dir = 'Example_hotspot'

        # Adding service addresses to walledgarden
        rb.add_to_walled_garden('*example.com')
        rb.add_to_walled_garden('login.example.com')

        # Adding server IP to ip walled garden
        rb.add_to_ip_walled_garden(config.EXAMPLE_SRV_IP)

        # Adding example RADIUS server
        rb.add_radius(
            service='hotspot',
            authentication_port='1812',
            accounting_port='1813',
            secret=config.RADIUS_SECRET,
            address=config.RADIUS_ADDR
        )
        print('radius added')

        if version.major == 6 and version.minor >= 34:
            print('new version detected')
            rb.add_hotspot_profile(
                name=hs_profile_name,
                dns_name='hs.example.com',
                hotspot_address=bridge_address[:-3],
                html_directory='flash/Example_hotspot' if use_flash_dir else 'Example_hotspot',
                login_by='mac,http-pap',
                trial_uptime_limit='2h',
                trial_uptime_reset='3h',
                trial_user_profile=hs_user_profile_name,
                mac_auth_mode='mac-as-username',
                radius_mac_format='XX:XX:XX:XX:XX:XX',
                use_radius='true'
            )

        else:
            print('old version detected')
            rb.add_hotspot_profile(
                name=hs_profile_name,
                dns_name='hs.example.com',
                hotspot_address=bridge_address[:-3],
                html_directory='flash/Example_hotspot' if use_flash_dir else 'Example_hotspot',
                login_by='mac,http-pap',
                trial_uptime='2h/3h',
                trial_user_profile=hs_user_profile_name,
                mac_auth_mode='mac-as-username',
                radius_mac_format='XX:XX:XX:XX:XX:XX',
                use_radius='true'
            )

        print('Hotspot server profile is set.')

        # hs_name = 'Example'
        rb.add_hotspot(hotspot.identity, bridge_name, hs_profile_name, pool_name)
        # wait some time before nat rules appear
        time.sleep(2)
        # setting up rule to redirect hotspot DNS requests
        nat = rb._api.get_resource('/ip/firewall/nat')
        insert_before_id = nat.get(comment='place hotspot rules here')[-1]['id']

        # udp
        nat.add(
            chain='pre-hotspot', protocol='udp', dst_port='53',
            action='dst-nat', to_addresses=config.DNS_ADDR,
            place_before=insert_before_id
        )
        # tcp
        nat.add(
            chain='pre-hotspot', protocol='tcp', dst_port='53',
            action='dst-nat', to_addresses=config.DNS_ADDR,
            place_before=insert_before_id
        )

        # Don't forget to add ip to walled garden, or packets will be dropped.
        rb.add_to_ip_walled_garden(config.DNS_ADDR)

        print('Hotspot server is up.')
        print('Done!')
        resp.status = falcon.HTTP_OK
        resp.body = json.dumps({'hotspot': hotspot.as_dict()})
