
import pandas as pd
from scraper.scraper import Scraper

def get_api_url_for(url, item):
        first_part = 'https://gateway.gofundme.com/web-gateway/v1/feed/'
        last_part = '/' + str(item)

        middle_part = url.replace('https://www.gofundme.com/f/', '')

        api_url = first_part + middle_part + last_part

        return api_url

def get_template():
    table = pd.read_csv('template.csv')
    table.drop(['Unnamed: 0'], axis=1, inplace = True)
    return table

def get_urls(size, offset=0):
    urls = []
    with open('url_extractor/url_list.txt', 'r') as file:
        count_offset = 1
        count = 1
        for line in file:
            if count_offset <= offset:
                count_offset += 1
                continue
            else:
                if count == size:
                    break
                count += 1
                line = line.replace('\n', '')
                urls.append(line)
                urls.append(get_api_url_for(line, 'counts'))
                urls.append(get_api_url_for(line, 'updates'))
                urls.append(get_api_url_for(line, 'comments'))

    return urls

import sys
import eventlet 
if sys.version_info[0]==2:
    import six
    from six.moves.urllib import request
if sys.version_info[0]==3:
    from eventlet.green.urllib import request
import random
import socket
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

super_proxy = socket.gethostbyname('zproxy.lum-superproxy.io')

class SingleSessionRetriever:

    url = "http://%s-unblocker-session-%s:%s@"+super_proxy+":%d"
    port = 22225

    def __init__(self, username, password, requests_limit, failures_limit):
        self._username = username
        self._password = password
        self._requests_limit = requests_limit
        self._failures_limit = failures_limit
        self._reset_session()

    def _reset_session(self):
        session_id = random.random()
        proxy = SingleSessionRetriever.url % (self._username, session_id, self._password,
                                              SingleSessionRetriever.port)
        proxy_handler = request.ProxyHandler({'http': proxy, 'https': proxy})
        self._opener = request.build_opener(proxy_handler)
        self._requests = 0
        self._failures = 0

    def retrieve(self, url, timeout):
        while True:
            if self._requests == self._requests_limit:
                self._reset_session()
            self._requests += 1
            try:
                timer = eventlet.Timeout(timeout)
                result = self._opener.open(url).read()
                timer.cancel()
                return result
            except:
                timer.cancel()
                self._failures += 1
                if self._failures == self._failures_limit:
                    self._reset_session()

class MultiSessionRetriever:
    def __init__(self, username, password, session_requests_limit, session_failures_limit):
        self._username = username
        self._password = password
        self._sessions_stack = []
        self._session_requests_limit = session_requests_limit
        self._session_failures_limit = session_failures_limit

    def retrieve(self, urls, timeout, parallel_sessions_limit, callback):
        pool = eventlet.GreenPool(parallel_sessions_limit)
        counter = 0
        for url, body in pool.imap(lambda url: self._retrieve_single(url, timeout), urls):
            counter = callback(url, body, counter)
           

    def _retrieve_single(self, url, timeout):
        if self._sessions_stack:
            session = self._sessions_stack.pop()
        else:
            session = SingleSessionRetriever(self._username, self._password,
                                             self._session_requests_limit, self._session_failures_limit)
        body = session.retrieve(url, timeout)
        self._sessions_stack.append(session)
        return url, body

counter=0
main_url = ''
html = ''
counts = ''
updates = ''
comments = ''
table = get_template()

def output(url, body, counter):
    if counter == 0:
        global main_url
        main_url = url
        global html 
        html = body
        return counter + 1
    elif counter == 1:
        global counts 
        counts = body
        return counter + 1
    elif counter == 2:
        global updates 
        updates = body
        return counter + 1
    else:
        comments = body
        scraper = Scraper(main_url, html, counts, updates, comments)
        scraper.start()
        row = scraper.get_dictionary()
        global table
        table = table.append(row, ignore_index = True)
        return 0


limit = int(input('How many urls?')) + 1
offset = int(input('How much offset?'))


urls = get_urls(limit, offset)

n_total_req = 1
req_timeout = 10
n_parallel_exit_nodes = 100
switch_ip_every_n_req = 10
max_failures = 2

multiRetriever = MultiSessionRetriever('lum-customer-a_bubutanu-zone-gofundme_com-route_err-pass_dyn', 'GFMscraper1', switch_ip_every_n_req, max_failures)

multiRetriever.retrieve(urls * n_total_req, req_timeout, n_parallel_exit_nodes, output)

print('Scraping successful')

table.to_csv('{filename}.csv'.format(filename=input('File name:')))
print('Successful export')

# API calls problem: those are URLs too!