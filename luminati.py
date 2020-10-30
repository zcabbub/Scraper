#!/usr/bin/env python
print('If you get error "ImportError: No module named \'six\'" install six:\n'+\
    '$ sudo pip install six');
print('To enable your free eval account and get CUSTOMER, YOURZONE and ' + \
    'YOURPASS, please contact sales@luminati.io')

import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

if sys.version_info[0]==2:
    import six
    from six.moves.urllib import request
    opener = request.build_opener(
        request.ProxyHandler(
            {'http': 'http://lum-customer-a_bubutanu-zone-gofundme_com-country-us-unblocker:1xavrej2f0hu@zproxy.lum-superproxy.io:22225',
            'https': 'http://lum-customer-a_bubutanu-zone-gofundme_com-country-us-unblocker:1xavrej2f0hu@zproxy.lum-superproxy.io:22225'}))
    content = opener.open('https://www.gofundme.com/f/rich-de-croce-memorial-fund').read()
    
    with open('test.html', 'w') as file:
        file.write(str(content))

    print('Done.')

if sys.version_info[0]==3:
    import urllib.request
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(
            {'http': 'http://lum-customer-a_bubutanu-zone-gofundme_com-country-us-unblocker:GFMscraper1@zproxy.lum-superproxy.io:22225',
            'https': 'http://lum-customer-a_bubutanu-zone-gofundme_com-country-us-unblocker:GFMscraper1@zproxy.lum-superproxy.io:22225'}))
    content = opener.open('https://www.gofundme.com/f/rich-de-croce-memorial-fund').read()
    
    with open('test.html', 'w') as file:
        file.write(str(content))
    
    print('Done.')