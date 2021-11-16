import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.common.exceptions import NoSuchElementException
import csv
from timeit import default_timer as timer
from datetime import timedelta
import random
import re
import os
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless") # launching web driver in headless mode



# ---------------       EDIT THESE VARIABLES        ---------------
COOKIE = '' # FOLLOW README
DRIVER_PATH = '/path/to/driver' # PATH TO YOUR CHROME DRIVER HERE
TOWNS = ['New+York,NY', # LIST OF TOWNS
         'Tulsa,OK'
         ]
kw_list = ['gym', 'movie+theater'] # KEYWORD SEARCH ITEMS



 # create /scrapes folder:
local_path = '/scrapes'
def check_for_dir(path):
    cwd = os.getcwd()
    if not os.path.exists(cwd + path):
        os.makedirs(cwd + path)
check_for_dir(local_path) # you can delete this after first run



def scrape_yelp(keyword, location):
    start = timer() # timing our function

    '''

    Scrapes all pages of Yelp.com search of 'keyword' in 'location'

    Returns dataframe containing business information, including:
        name, website, phone number, physical address, category(s), number of reviews, & star rating

    '''


    def check(frame): # checking size of data found, used in exporting to excel
        df = frame
        row_size = df.shape[0]
        if  row_size <= 2:
            return False
        else:
            return True


    pages_url = f'https://www.yelp.com/search?find_desc={keyword}&find_loc={location}&start=0'
    headers = {
        'authority': 'www.yelp.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'cookie': COOKIE
    }
    response = requests.request("GET", pages_url, headers=headers, data={}).text
    soup = BeautifulSoup(response, 'lxml')


    pages = soup.select('div[class *= "pagination-link-container"]')
    num_pages = int(len(pages) - 1)

    scraped_details = []

    for page in range(num_pages):


        url = f'https://www.yelp.com/search?find_desc={keyword}&find_loc={location}&start={page}0'
        print(f'Scraping page {page} of search: {url}')
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)
        driver.get(url)

        # List of links to Yelp business pages
        link_elements = driver.find_elements_by_class_name('css-1422juy')
        link_list = [x.get_attribute('href') for x in link_elements]


        for link in link_list: # going to each business page on current search page
            driver.get(link)
            print(f'Scraping {link}...')
            time.sleep(2) # always good practice to limit rate of requests somewhat
            response = requests.request("GET", link, headers=headers, data={}).text
            soup = BeautifulSoup(response, 'lxml')

            # NAME OF ESTABLISHMENT
            try:
                name = soup.select('h1[class *= "css-1x9iesk"]')
                name = [x.text for x in name][0]
            except:
                name = None

            # WEBSITE
            try:
                site = driver.find_element_by_partial_link_text('://')
                site = site.get_attribute('href')
                site = site.split('%3A%2F%2F', 1)[1] # removes content before site link
                site = site.split('&cachebuster', 1)[0] # removes content after site link
                if '%2F' in site:
                    site = site.split('%2F', 1)[0] # removing more unnecessary stuff in URL string
                else:
                    pass
            except NoSuchElementException:
                continue # if they don't have a website listed... we don't care

            # PHONE NUMBER
            try:
                sidebar = soup.select("div.css-xp8w2v")
                phone = [ele.find(text=re.compile('Phone number')).findNext('p').text for ele in sidebar][0]
            except:
                phone = None

            # ADDRESS
            try:
                sidebar = soup.select("div.css-xp8w2v")
                address = [ele.find(text=re.compile('Get Directions')).findNext('p').text for ele in sidebar][0]
            except:
                address = None

            # CATEGORIES
            try:
                cats = soup.select("span.css-oe5jd3")
                cats = [ele.select("a.css-1422juy") for ele in cats]
                cats = [ele[0].text for ele in cats if ele]
            except:
                cats = None

            # NUMBER OR REVIEWS
            try:
                num_revs = soup.select("span.css-oe5jd3")
                num_revs = [ele.find(text=re.compile(' review')) for ele in num_revs]
                num_revs = [ele for ele in num_revs if ele][0]
            except:
                num_revs = None

            # STAR RATING
            try:
                stars = soup.select("span.display--inline__09f24__c6N_k")
                stars = [ele.select("div.i-stars__09f24__foihJ") for ele in stars]
                stars = [ele for ele in stars if ele][0][0]['aria-label']
            except:
                stars = None

            business_details = {'name': name,
                                'website': site,
                                'phone': phone,
                                'address': address,
                                'categories': cats,
                                'number_of_reviews': num_revs,
                                'star_rating': stars
                                }
            scraped_details.append(business_details)

    scraped_details = pd.DataFrame(scraped_details)
    scraped_details = scraped_details.drop_duplicates(subset=['address', 'website',])
    time.sleep(random.randint(0, 3)) # wait 0-3 seconds after each search

    CHECK = check(scraped_details)
    for retries in range(2):
        if CHECK == True: # if data is found -> export to excel
            scraped_details.to_excel(f'scrapes/{keyword}_{location}_YELP.xlsx')
            print(f'Writing new file:  {keyword}_{location}_YELP.xlsx')
        else: # if data isn't found -> do nothing & move on
            print(f'Not enough data to scrape. Not creating new file for {keyword} in {location}.')
        break

    # timing each scrape and recording times in .CSV file
    stop = timer()
    elapsed = str(timedelta(seconds=stop - start))
    file_name = f'{keyword}_{location}_YELP.xlsx'
    num_rows = scraped_details.shape[0]
    with open('scrape_stats.csv', 'a+', newline='') as f:  #
        w = csv.writer(f)
        w.writerow([file_name] + [elapsed] + [str(num_rows) + ' rows'])
        f.close()


# wrapper function to run scrape for each location + keyword combination
def batch_scrape():
    kw_town_list = [(kw, town) for kw in kw_list for town in TOWNS]
    for kw_town in kw_town_list:
        scrape_yelp(kw_town[0], kw_town[1])


# batch_scrape()






















