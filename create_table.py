# import packages
import pandas as pd
from scraper.scraper import Scraper

import time
start_time = time.time()

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
                urls.append(line)

    urls = [url.replace('\n', '') for url in urls]

    return urls

def fill_template(template, urls):
    table = template
    for url in urls:

        scraper = Scraper(url)
        times = 0
        
        while(True):
            if times < 5:    
                try:                
                    scraper.start()
                    row = scraper.get_dictionary()
                    table = table.append(row, ignore_index=True)
                    break
                except:
                    continue
                times += 1
            else:
                print('5 unsuccessful attempts')
                break

    return table


limit = int(input('How many urls?')) + 1
offset = int(input('How much offset?'))

print('Start filling the table...')

template = get_template()
urls = get_urls(limit, offset)

table = fill_template(template, urls)
print('Successful scraping')

table.to_csv('{filename}.csv'.format(filename=input('File name:')))
print('Successful export')

print("Process finished --- %s seconds ---" % (time.time() - start_time))

# ### PROBLEMS:
# 1. If something goes wrong, the program should export everything it already scraped
#  - maybe solve by inserting each row in the table and then export the table regardless of errors,
#    when the program finishes
# 2. Let's keep it at 35 000 rows/file. Make each part look like this: '2020-10-10_part_X.csv'