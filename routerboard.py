import os
import rosapi
import paramiko
import config


class RouterboardUploader:
    def __init__(self, hotspot):
        self._address = hotspot.vpn_user.get_ip_string()
        self._port = 22022

    def connect(self):
        self._transport = paramiko.Transport((self._address, self._port))
        self._transport.connect(username=config.API_USER_NAME, password=config.API_USER_PASSWORD)

    def close(self):
        self._transport.close()

    def upload_file(self, src, dst_dir):
        sftp = paramiko.SFTPClient.from_transport(self._transport)
        dst_path = os.path.join(dst_dir, src)
        sftp.put(src, dst_path)
        sftp.close()

    def upload_folder(self, src, dst_dir):
        sftp = paramiko.SFTPClient.from_transport(self._transport)
        os.chdir(os.path.split(src)[0])
        parent = os.path.split(src)[1]
        for walker in os.walk(parent):
            try:
                sftp.mkdir(os.path.join(dst_dir, walker[0]))
            except:
                pass
            for file in walker[2]:
                sftp.put(os.path.join(walker[0], file), os.path.join(dst_dir, walker[0], file))
        sftp.close()

    def flash_dir_is_available(self):
        sftp = paramiko.SFTPClient.from_transport(self._transport)
        available = 'flash' in sftp.listdir()
        sftp.close()
        return available


class HotspotUserAbsent(Exception):
    pass


class RBVersion:
    def __init__(self, version_string):
        self.fix = 0
        if len(version_string.split('.')) == 3:
            major, minor, fix = version_string.split('.')
            self.major, self.minor, self.fix = int(major), int(minor), int(fix)
        else:
            major, minor = version_string.split('.')
            self.major, self.minor = int(major), int(minor)

    def __str__(self):
        return 'major = {0}, minor = {1}, fix = {2}'.format(self.major, self.minor, self.fix)

    def __repr__(self):
        return self.__str__()


class RB:
    def __init__(self, rosapi):
        self._api = rosapi

    @classmethod
    def connect(cls, address, username, password, port=8728):
        try:
            api = rosapi.RouterboardAPI(address, username=username, password=password, port=port)
        except rosapi.RosAPIConnectionError:
            print('Cannot connect, please check address and port')
            raise
        except rosapi.RosAPIError:
            print('Check username and password')
            raise
        else:
            return cls(api)

    @classmethod
    def from_hotspot(cls, hotspot):
        try:
            host = hotspot.vpn_user.get_ip_string() if hotspot.vpn_user is not None else hotspot.hostname
            api = rosapi.RouterboardAPI(host,
                                        username=config['API_USER_NAME'],
                                        password=config['API_USER_PASSWORD'],
                                        port=8728)
        except rosapi.RosAPIConnectionError:
            print('Cannot connect, please check address and port')
            raise
        except rosapi.RosAPIError:
            print('Check username and password')
            raise
        else:
            return cls(api)

    def cleanup_users_and_groups(self, groupname, username):
        print('Performing Users and Groups cleanup')

        users = self._api.get_resource('/user')

        users_sel = users.get(group=groupname)
        if len(users_sel) > 0:
            for u in users_sel:
                users.remove(id=u['id'])

        groups = self._api.get_resource('/user/group')

        groups_sel = groups.get(name=groupname)
        if len(groups_sel) > 0:
            for g in groups_sel:
                groups.remove(id=g['id'])


    def cleanup(self):
        print('Performing cleanup')
        hs_user_profiles = self._api.get_resource('/ip/hotspot/user/profile')
        hs_user_profiles_sel = hs_user_profiles.get(name='ExampleUSR')
        if len(hs_user_profiles_sel) > 0:
            print('Found hotspot user profile. Removing')
            for prof in hs_user_profiles_sel:
                hs_user_profiles.remove(id=prof['id'])

        walled_garden = self._api.get_resource('/ip/hotspot/walled-garden')
        for host in ['*example.com', 'login.example.com']:
            print('Found walled garden record. Removing')
            walled_garden_sel = walled_garden.get(dst_host=host)
            if len(walled_garden_sel) > 0:
                for wgrec in walled_garden_sel:
                    walled_garden.remove(id=wgrec['id'])

        hs_profiles = self._api.get_resource('/ip/hotspot/profile')
        hs_profiles_sel = hs_profiles.get(name='ExampleHSProfile')
        if len(hs_profiles_sel) > 0:
            print('Found hotspot profile. Removing')
            for hsprof in hs_profiles_sel:
                hs_profiles.remove(id=hsprof['id'])

        hotspots = self._api.get_resource('/ip/hotspot')
        hotspots_sel = hotspots.get(interface='ExampleBR')
        if len(hotspots_sel) > 0:
            print('Found hotspot. Removing')
            for hotspot in hotspots_sel:
                hotspots.remove(id=hotspot['id'])

        pools = self._api.get_resource('/ip/pool')
        pools_sel = pools.get(name='ExamplePOOL')
        if len(pools_sel) > 0:
            print('Found pool. Removing')
            for pool in pools_sel:
                pools.remove(id=pool['id'])

        addresses = self._api.get_resource('/ip/address')
        addresses_sel = addresses.get(interface='ExampleBR')
        if len(addresses_sel) > 0:
            print('Found address. Removing')
            for adr in addresses_sel:
                addresses.remove(id=adr['id'])

        dhcp_networks = self._api.get_resource('/ip/dhcp-server/network')
        dhcp_networks_sel = dhcp_networks.get(address='10.100.0.0/16')
        if len(dhcp_networks_sel) > 0:
            print('Found dhcp network. Removing')
            for net in dhcp_networks_sel:
                dhcp_networks.remove(id=net['id'])

        dhcp_servers = self._api.get_resource('/ip/dhcp-server')
        dhcp_servers_sel = dhcp_servers.get(name='ExampleDHCP')
        if len(dhcp_servers_sel) > 0:
            print('Found dhcp server. Removing')
            for srv in dhcp_servers_sel:
                dhcp_servers.remove(id=srv['id'])

        bridge_ports = self._api.get_resource('/interface/bridge/port')
        bridge_ports_sel = bridge_ports.get(bridge='ExampleBR')
        if len(bridge_ports_sel) > 0:
            print('Found bridge ports. Removing')
            for bp in bridge_ports_sel:
                bridge_ports.remove(id=bp['id'])

        bridges = self._api.get_resource('/interface/bridge')
        bridges_sel = bridges.get(name='ExampleBR')
        if len(bridges_sel):
            print('Found bridge. Removing')
            for br in bridges_sel:
                bridges.remove(id=br['id'])

        nat_rules = self._api.get_resource('/ip/firewall/nat')
        nat_rules_sel = nat_rules.get(action='masquerade', src_address='10.100.0.0/16')
        if len(nat_rules_sel) > 0:
            print('Found nat masquerade rule. Removing')
            for rule in nat_rules_sel:
                nat_rules.remove(id=rule['id'])

        security_profiles = self._api.get_resource('/interface/wireless/security-profiles')
        security_profiles_sel = security_profiles.get(name='ExampleSP')
        if len(security_profiles_sel) > 0:
            print('Found security profiles. Removing')
            for sp in security_profiles_sel:
                security_profiles.remove(id=sp['id'])

        wlans = self._api.get_resource('/interface/wireless')
        wlans_sel = wlans.get(name='ExampleAP')
        if len(wlans_sel) > 0:
            print('Found VirtualAPs. Removing')
            for wlan in wlans_sel:
                wlans.remove(id=wlan['id'])

        radiuses = self._api.get_resource('/radius')
        radiuses_sel = radiuses.get(address=config.RADIUS_ADDR)
        for rad in radiuses_sel:
            radiuses.remove(id=rad['id'])

        dns_static = self._api.get_resource('/ip/dns/static')
        dns_recs = dns_static.get(name='captive.apple.com')
        for rec in dns_recs:
            dns_static.remove(id=rec['id'])

    def get_version(self):
        packages = self._api.get_resource('/system/package')
        pkg = packages.get(id='*1')
        version_string = pkg[0]['version']
        return RBVersion(version_string)

    def add_dns_static_record(self, name, address):
        dns_static = self._api.get_resource('/ip/dns/static')
        dns_static.add(name=name, address=address)

    def add_radius(self, **kwargs):
        radiuses = self._api.get_resource('/radius')
        radiuses.add(**kwargs)

    def add_hotspot_user(self, hotspot_user):
        hotspot_users = self._api.get_resource('/ip/hotspot/user')
        try:
            hotspot_users.add(name=hotspot_user.login, password=hotspot_user.password)
        except:
            raise

    def add_virtual_ap(self, **kwargs):
        raise NotImplementedError

    def add_wireless_security_profile(self, **kwargs):
        security_profiles = self._api.get_resource('/interface/wireless/security-profiles')
        security_profiles.add(**kwargs)

    def delete_hotspot_user(self, hotspot_user):
        hotspot_users = self._api.get_resource('/ip/hotspot/user')
        props = hotspot_users.get(name=hotspot_user.login, _props='.id')
        if len(props) > 0:
            user_id = props[0]['id']
            hotspot_users.remove(id=user_id)
        else:
            raise HotspotUserAbsent()

    def list_interfaces(self):
        bridge_ports = self._api.get_resource('/interface/bridge/port')
        port_names = [port['interface'] for port in bridge_ports.get()]

        ethers = self._api.get_resource('/interface/ethernet')
        wireless = self._api.get_resource('/interface/wireless')
        results = {
            'ethers': [],
            'wlans': []
        }

        for eth in ethers.get():
            if eth['name'] in port_names\
            or ('master-port' in eth and eth['master-port'] != 'none')\
            or ('slave' in eth and eth['slave'] == 'true'):
                results['ethers'].append({'name': eth['name'], 'enabled': False})
            else:
                results['ethers'].append({'name': eth['name'], 'enabled': True})

        for w in wireless.get():
            if w['name'] in port_names:
                results['wlans'].append({'name': w['name'], 'enabled': False})
            else:
                results['wlans'].append({'name': w['name'], 'enabled': True})

        return results

    def get_interface_names(self):
        ethers = self._api.get_resource('/interface/ethernet')
        wireless = self._api.get_resource('/interface/wireless')
        return [i['name'] for i in ethers.get() + wireless.get()]

    def add_group(self, name, permissions):
        groups = self._api.get_resource('/user/group')
        groups.add(name=name, policy=permissions)

    def add_user(self, username, password, group, address):
        users = self._api.get_resource('/user')
        users.add(name=username, group=group, password=password, address=address)

    def enable_ssh(self):
        fw_rules = self._api.get_resource('/ip/firewall/filter')
        fw_rules.add(chain='input', protocol='tcp', dst_port='22022', action='accept', place_before='0')
        services = self._api.get_resource('/ip/service')
        services.set(numbers='ssh', disabled='no', port='22022')

    def add_bridge(self, name, interfaces):
        if type(interfaces) != list:
            print("interfaces should be list of strings ['eth1','eth2','eth4']")
            return
        bridges = self._api.get_resource('/interface/bridge')
        bridges.add(name=name)

        ports = self._api.get_resource('/interface/bridge/port')
        for iface in interfaces:
            ports.add(bridge=name, interface=iface)

    def add_pool(self, name, ranges):
        pools = self._api.get_resource('/ip/pool')
        pools.add(name=name, ranges=ranges)

    def add_dhcp_network(self, network, server_address):
        dhcp_networks = self._api.get_resource('/ip/dhcp-server/network')
        dhcp_networks.add(address=network, dns_server=server_address, gateway=server_address)

    def add_dhcp_srv(self, name, interface, pool):
        dhcp_servers = self._api.get_resource('/ip/dhcp-server')
        dhcp_servers.add(name=name, interface=interface, address_pool=pool, disabled='no')

    def add_address(self, interface, address):
        addresses = self._api.get_resource('/ip/address')
        addresses.add(interface=interface, address=address)

    def enable_masquerade(self, addresses):
        nat_rules = self._api.get_resource('/ip/firewall/nat')
        nat_rules.add(chain='srcnat', action='masquerade', src_address=addresses)

    def add_to_walled_garden(self, target):
        wg = self._api.get_resource('/ip/hotspot/walled-garden')
        wg.add(action='allow', dst_host=target)

    def add_to_ip_walled_garden(self, ip_address):
        ipwg = self._api.get_resource('/ip/hotspot/walled-garden/ip')
        ipwg.add(action='accept', dst_address=ip_address)

    def add_hotspot_user_profile(self, **kwargs):
        profiles = self._api.get_resource('/ip/hotspot/user/profile')
        profiles.add(**kwargs)

    def add_hotspot_profile(self, **kwargs):
        hs_profiles = self._api.get_resource('/ip/hotspot/profile')
        hs_profiles.add(**kwargs)

    def add_hotspot(self, name, interface, profile, pool):
        hotspots = self._api.get_resource('/ip/hotspot')
        hotspots.add(name=name, interface=interface, profile=profile, address_pool=pool, disabled='no')

    def add_certificate(self, filepath, passphrase=''):
        certificates = self._api.get_resource('/certificate')
        args = {
            'file-name': filepath,
        }
        certificates.call('import', args)

    def get_certificate(self, common_name):
        certificates = self._api.get_resource('/certificate')
        return certificates.get(common_name='hs.example.com')[0]['name']
