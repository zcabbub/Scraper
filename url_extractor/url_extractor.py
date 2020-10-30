# import packages
from bs4 import BeautifulSoup
import requests
import gzip
from io import BytesIO
import urllib.request as urllib
import pandas as pd

#load this index-sitemap
r = requests.get("https://www.gofundme.com/sitemap.xml")
xml = r.text
soup = BeautifulSoup(xml,"lxml")
sitemapTags = soup.find_all("sitemap")

urls_list = []
urls_total = 0

#loop to find all sub-sitemap URLs

for sitemap in sitemapTags:
    subsitemap = sitemap.findNext("loc").text
    print(subsitemap)

    #load and handle the gzip stuff to get a proper XML
    request = urllib.Request(subsitemap)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib.urlopen(request)

    buf = BytesIO(response.read())
    f = gzip.GzipFile(fileobj=buf)
    data = f.read()

    soup2 = BeautifulSoup(str(data),"lxml")
    urlTags = soup2.find_all("url")
    urls_total = urls_total + int(len(urlTags))
    print(str(urls_total) + " - " + str(len(urlTags)))

    #Loop URLs withing ever sub-sitemap
    for url in urlTags:
        urls_list.append(url.findNext("loc").text)


#df = pd.DataFrame({'urls_list': urls_list,'lastmod_list': lastmod_list,'changefreq_list': changefreq_list})
#df

with open('url_list.txt', 'w') as file:
    file.writelines('\n'.join(urls_list))
