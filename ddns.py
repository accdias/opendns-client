#!/usr/bin/python3
from requests import get as http_get
from configparser import ConfigParser
from pathlib import Path
from time import time

__author__ = 'Antonio Dias'
__email__ = 'accdias@gmail.com'
__copyright__ = 'Copyright 2018, Antonio Dias'
__license__ = 'GPL'
__version__ = '0.1'
__status__ = 'Development'

ddns_config_file = Path('~/.ddns/config').expanduser()
ddns_cache_file = Path('/var/tmp/ddns.cache')

ddns_user_agent = f'CloudPro - Python DDNS Client - {__version__}'

# Load the main configuration file
config = ConfigParser(allow_no_value=True)
config.read(ddns_config_file)

# Default timeout is 7 days in seconds
timeout = 60 * 60 * 24 * 7

# DuckDNS update URL
duckdns_update_url = 'https://www.duckdns.org/update?domains={YOURVALUE}&token={YOURVALUE}[&ip={YOURVALUE}][&ipv6={YOURVALUE}][&verbose=true][&clear=true]'

# OpenDNS (DNSoMatic) update URL
ddns_update_url = 'https://updates.dnsomatic.com/nic/update'

ddns_update_auth = (config.get('opendns', 'account'), config.get('opendns', 'password'))

ddns_update_payload = {
    'hostname': config.get('opendns', 'hostname'),
    'myip': '',
    'wildcard': 'NOCHG',
    'mx': 'NOCHG',
    'backmx': 'NOCHG',
    'user-agent': ddns_user_agent
}

# public_ipv4_json_url = 'http://v4.ifconfig.co/json'
# public_ipv6_json_url = 'http://v6.ifconfig.co/json'
# public_ipv4_url = 'http://v4.ifconfig.co/ip'
# public_ipv6_url = 'http://v6.ifconfig.co/ip'
public_ipv4_url = 'http://myip.dnsomatic.com'

with http_get(public_ipv4_url) as r:
    ddns_update_payload['myip'] = r.text.strip() if r.ok else None
    if not ddns_update_payload['myip']:
        print('Could not determine public IP address')
        exit(1)

if ddns_cache_file.exists():
    with ddns_cache_file.open() as f:
        last_update, cached_ip = f.readline().strip().split(':')
        last_update = float(last_update)
else:
    last_update, cached_ip = 0, None

if (cached_ip != ddns_update_payload['myip']) or (time() - last_update > timeout):
    with ddns_cache_file.open('w') as f:
        f.write(f'{time()}:{ddns_update_payload["myip"]}')
    with http_get(ddns_update_url, data=ddns_update_payload, auth=ddns_update_auth) as r:
        if r.ok:
            print(f'Address updated: {ddns_update_payload["myip"]}')
        else:
            print(r.text)
else:
    print(f'Address hasn\'t changed: {cached_ip}')

# vim:ts=4:sts=4:sw=4:et
