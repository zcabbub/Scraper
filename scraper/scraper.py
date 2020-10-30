# coding: utf-8

import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup

from re import sub, findall
from decimal import Decimal

from urllib.error import URLError

class Scraper():
     # INIT:

    # def __init__(self, url):
    #     Scraper._counter+=1
    #     self.url = url

    def __init__(self, url, body):
        self.url = url
        self.html = body

    # FINDERS:

    ## HTML
    # def scrape_html(self):
    #     html = requests.get(self.url)
    #     status_code = html.status_code

    #     if status_code > 199 and status_code < 300:
    #         html = html.text
    #         return html
    #     elif status_code > 399 and status_code < 600:
    #         print(status_code)
    #         raise URLError('Connection failed: site cannot be reached - CODE: {code}'.format(code=status_code))
    #     else:
    #         print(status_code)
    #         raise ConnectionError('Connection failed - redirect error - CODE: {code}'.format(code=status_code))

    def make_soup(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        return soup

    def find_title(self):
        soup = self.soup
        try:
            title = soup.find(attrs={'class' : 'a-campaign-title'}).text
        except:
            title = None
        return title

    def find_category(self):
        soup = self.soup
        try:
            category = soup.find('div', attrs={'class' : 'm-campaign-byline-meta'}).find('a', attrs={'class' : 'm-campaign-byline-type'}).text
        except:
            category = None
        return category

    def find_category_url(self):
        soup = self.soup
        try:
            url = soup.find(attrs={'class' : 'm-campaign-byline-meta'}).find('a', attrs={'class' : 'm-campaign-byline-type'})['href']
            category_url = 'https://www.gofundme.com' + url
        except:
            category_url = None
        return category_url

    def find_currency(self):
        soup = self.soup
        try:
            raw_raised_goal = soup.find('h2', attrs={'class' : 'm-progress-meter-heading'}).text.split(' ')
            money = raw_raised_goal[0]
            if money[1].isdigit():
                currency = money[0]
            else:
                currency = money[0:2]
        except:
            currency = None
        return currency

    def find_goal(self):
        soup = self.soup
        try:
            raw_raised_goal = soup.find('h2', attrs={'class' : 'm-progress-meter-heading'}).span.text.split(' ')
            if len(raw_raised_goal) < 3:
                return None
            else:
                money = raw_raised_goal[2]
                goal = int(Decimal(sub(r'[^\d.]', '', money)))
        except:
            goal = None
        return goal

    def find_raised(self):
        soup = self.soup
        try:
            raw_raised_goal = soup.find('h2', attrs={'class' : 'm-progress-meter-heading'}).text.split(' ')
            money = raw_raised_goal[0]
            raised = int(Decimal(sub(r'[^\d.]', '', money)))
        except:
            raised = None
        return raised
        

    def find_description(self):
        soup = self.soup
        try:
            description = soup.find('div', attrs={'class': 'o-campaign-story'}).text
        except:
            description = None
        return description

    def find_creation_date(self):
        soup = self.soup
        try:
            raw_creation_date = soup.find('span', attrs={'class' : 'm-campaign-byline-created'}).text.split(' ')
            if 'ago' in raw_creation_date:
                days_to_subtract = int(raw_creation_date[1])
                creation_date = (datetime.today() - timedelta(days=days_to_subtract)).date()
            else:
                date_string = ' '.join(raw_creation_date[1:])
                creation_date = str(datetime.strptime(date_string, "%B %d, %Y").date())
        except:
            creation_date=None
        return creation_date

    def find_organizers(self):
        soup = self.soup

        try:
            organizer = {}

            organizer_type = soup.find('div', attrs={'class' : 'm-campaign-members-header-title'}).text

            if 'team' in organizer_type:
                organizer['Type'] = 'Team'
                organizer['Members'] = int(findall(r"\(\s*\+?(-?\d+)\s*\)", organizer_type)[0])
            else:
                organizer['Type'] = 'Individual'
                organizer['Members'] = None

            organizer['Organizer'] = soup.find('div', attrs={'id' : 'campaign-members'}).find('div', attrs={'class' : 'm-person-info-name'}).text.replace(u'\xa0', u'')

            beneficiary = soup.find('div', attrs={'class' : 'm-campaign-members-main-beneficiary'})
            if beneficiary:
                organization = beneficiary.find('div', attrs={'class' : 'm-organization-info'})
                if organization:
                    organizer['Beneficiary'] = organization.find('div', attrs={'class' : 'm-organization-info-content-child'}).text.replace(u'\xa0', u'')
                else:
                    organizer['Beneficiary'] = beneficiary.find('div', attrs={'class' : 'm-person-info-name'}).text.replace(u'\xa0', u'')
            else:
                organizer['Beneficiary'] = None

            if ':' in organizer_type:
                organizer['Team name'] = organizer_type.split(' ')[2:-1]
            else:
                organizer['Team name'] = None

            details = soup.find('div', attrs={'class' : 'o-campaign-members'}).find('div', attrs={'class' : 'm-person-info-content'}).find_all('div', attrs={'class' : 'text-small'})

            for div in details:
                if ', ' in div.text:
                    organizer['Location'] = div.text
                else:
                    organizer['Location'] = None
        except:
            organizer = None
        return organizer

    ## API calls

    ####create API url
    def get_api_url_for(self, item):
        first_part = 'https://gateway.gofundme.com/web-gateway/v1/feed/'
        last_part = '/' + str(item)

        middle_part = self.get_url().replace('https://www.gofundme.com/f/', '')

        api_url = first_part + middle_part + last_part

        return api_url

    def get_json_for(self, item):
        url = self.get_api_url_for(item)
        response = requests.get(url)
        json = response.json()
        return json
        # try:
        #     json['error']
        # except KeyError:
        #     return json
        # else:
        #     raise ValueError('Wrong path: {message}'.format(message = json['error']['short_description']))

    ### counts
    def find_counts(self):
        try:
            json = self.get_json_for('counts')
            if json['references'] == {}:
                counts = {}
            else: 
                counts = json['references']['counts']
        except:
            counts = None
        return counts

    def find_total_photos(self):
        json = self.counts_json
        return json['total_photos']

    def find_total_community_photos(self):
        json = self.counts_json
        return json['total_community_photos']

    def find_total_updates(self):
        json = self.counts_json
        return json['total_updates']

    def find_total_donations(self):
        json = self.counts_json
        return json['total_donations']

    def find_total_unique_donors(self):
        json = self.counts_json
        return json['total_unique_donors']

    def find_amount_raised_unattributed(self):
        json = self.counts_json
        return json['amount_raised_unattributed']

    def find_number_of_donations_unattributed(self):
        json = self.counts_json
        return json['number_of_donations_unattributed']

    def find_campaign_hearts(self):
        json = self.counts_json
        return json['campaign_hearts']

    def find_social_share_total(self):
        json = self.counts_json
        return json['social_share_total']


    ### updates
    def find_updates(self):
        json = self.get_json_for('updates')

        if 'error' in json:
            updates = None
        elif json['references'] == {}:
            updates = {}
        else:
            all_updates = json['references']['updates']
            updates = {}
            keys = ['Author', 'Author type', 'Text', 'Photos', 'Created_at']
            total_updates = len(all_updates)

            for i in range(total_updates):
                author = all_updates[i]['author']
                author_type = all_updates[i]['author_type']
                text = all_updates[i]['text']
                photos = [ photo['url'] for photo in all_updates[i]['photos'] ]
                created_at = all_updates[i]['created_at']

                values = [author, author_type, text, photos, created_at]

                updates[i] = dict(zip(keys, values))

        return updates


    ###comments
    def find_comments(self):
        json = self.get_json_for('comments')

        if 'error' in json:
            comments = None
        elif json['references'] == {}:
            comments = {}
        else:
            all_comments = json['references']['contents']
            comments = {}

            total_comments = len(all_comments)

            for i in range(total_comments):
                name = all_comments[i]['name']
                if 'donation' in all_comments[i]:
                    donation = all_comments[i]['donation']['amount']
                    comment = all_comments[i]['comment']['comment']
                    timestamp = all_comments[i]['comment']['timestamp']

                    keys = ['Name', 'Donation', 'Comment', 'Timestamp']
                    values = [name, donation, comment, timestamp]
                else:
                    comment = all_comments[i]['comment']['comment']
                    timestamp = all_comments[i]['comment']['timestamp']

                    keys = ['Name', 'Comment', 'Timestamp']
                    values = [name, comment, timestamp]

                comments[i] = dict(zip(keys, values))

        return comments


    ###photos
    def find_photos(self):
        json = self.get_json_for('photos')
        if json['references'] == {}:
            photos = {}
        else:
            all_photos = json['references']['photos']
            photos = [photo['url'] for photo in all_photos]

        return photos


    # STARTER function
    def start(self):
        print('Starting...')
        print(self.get_url())

        #HTML
        self.scraping_date = str(date.today())
        #self.html = self.scrape_html()
        self.soup = self.make_soup()
        self.title = self.find_title()
        self.category = self.find_category()
        self.category_url = self.find_category_url()
        self.currency = self.find_currency()
        self.goal = self.find_goal()
        self.raised = self.find_raised()
        self.description = self.find_description()
        self.creation_date = self.find_creation_date()
        self.organizers = self.find_organizers()

        #API calls
        ## counts:
        self.counts_json = self.find_counts()
        if self.counts_json != None:
            self.total_photos = self.find_total_photos()
            self.total_community_photos = self.find_total_community_photos()
            self.total_updates = self.find_total_updates()
            self.total_donations = self.find_total_donations()
            self.total_unique_donors = self.find_total_unique_donors()
            self.amount_raised_unattributed = self.find_amount_raised_unattributed()
            self.number_of_donations_unattributed = self.find_number_of_donations_unattributed()
            self.campaign_hearts = self.find_campaign_hearts()
            self.social_share_total = self.find_social_share_total()
        else:
            self.total_photos = None
            self.total_community_photos = None
            self.total_updates = None
            self.total_donations = None
            self.total_unique_donors = None
            self.amount_raised_unattributed = None
            self.number_of_donations_unattributed = None
            self.campaign_hearts = None
            self.social_share_total = None

        ## comments
        self.comments = self.find_comments()

        ## updates
        self.updates = self.find_updates()

        ## photos
        self.photos = self.find_photos()

        print("Done.")


    # GETTERS

    ## HTML
    def get_url(self):
        return self.url

    def get_html(self):
        return self.html

    def get_soup(self):
        return self.soup

    def get_scraping_date(self):
        return self.scraping_date

    def get_title(self):
        return self.title

    def get_category(self):
        return self.category

    def get_category_url(self):
        return self.category_url

    def get_goal(self):
        return self.goal

    def get_raised(self):
        return self.raised

    def get_currency(self):
        return self.currency

    def get_description(self):
        return self.description

    def get_creation_date(self):
        return self.creation_date

    def get_organizers(self):
        return self.organizers

    ## API calls

    # counts
    def get_total_photos(self):
       return self.total_photos
       
    def get_total_community_photos(self):
        return self.total_community_photos

    def get_total_updates(self):
        return self.total_updates

    def get_total_donations(self):
        return self.total_donations

    def get_total_unique_donors(self):
        return self.total_unique_donors

    def get_amount_raised_unattributed(self):
        return self.amount_raised_unattributed

    def get_number_of_donations_unattributed(self):
        return self.number_of_donations_unattributed

    def get_campaign_hearts(self):
        return self.campaign_hearts

    def get_social_share_total(self):
        return self.social_share_total

    # updates
    def get_updates(self):
        return self.updates

    # comments
    def get_comments(self):
        return self.comments

    # photos
    def get_photos(self):
        return self.photos

    # DICTIONARY
    def get_dictionary(self):
        dictionary = {'Scraping Date (YY-MM-DD)' : self.get_scraping_date(),
                      'URL' : self.get_url(),
                      'Title' : self.get_title(),
                      'Category' : self.get_category(),
                      'Category URL' : self.get_category_url(),
                      'Goal' : self.get_goal(),
                      'Raised' : self.get_raised(),
                      'Currency' : self.get_currency(),
                      'Description' : self.get_description(),
                      'Creation_date (YY-MM-DD)' : self.get_creation_date(),
                      'Organizers' : self.get_organizers(),
                      'No. of photos' : self.get_total_photos(),
                      'No. of community photos' : self.get_total_community_photos(),
                      'No. of donations' : self.get_total_donations(),
                      'No. of unique donors' : self.get_total_unique_donors(),
                      'Amount raised unattributed' : self.get_amount_raised_unattributed(),
                      'No. of donations unattributed' : self.get_number_of_donations_unattributed(),
                      'No. of campaign hearts' : self.get_campaign_hearts(),
                      'No. of social media shares' : self.get_social_share_total(),
                      'Updates' : self.get_updates(),
                      'Comments' : self.get_comments(),
                      'Photos' : self.get_photos()}
        return dictionary

    #PRINT
    def print_all(self):
        print('HTML \n')
        print(self.get_url())
        print(self.get_title())
        print(self.get_category())
        print(self.get_category_url())
        print(self.get_goal())
        print(self.get_raised())
        print(self.get_currency())
        print(self.get_description())
        print(self.get_creation_date())
        print(self.get_organizers())

        print('API calls \n')
        print('COUNTS')
        print(self.get_total_photos())
        print(self.get_total_community_photos())
        print(self.get_total_donations())
        print(self.get_total_unique_donors())
        print(self.get_amount_raised_unattributed())
        print(self.get_number_of_donations_unattributed())
        print(self.get_campaign_hearts())
        print(self.get_social_share_total())
        print('\n')

        print('UPDATES')
        print(self.get_updates())
        print('\n')

        print('COMMENTS')
        print(self.get_comments())
        print('\n')

        print('PHOTOS')
        print(self.get_photos())
        print('\n')
