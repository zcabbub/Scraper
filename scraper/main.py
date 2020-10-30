from scraper import Scraper

url = input('Type url to scrape:')

# creating the scraper
scraper = Scraper(url)

# starting scraping
scraper.start()

# print everything scraped
scraper.print_all()
