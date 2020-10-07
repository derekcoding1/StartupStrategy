from bs4 import BeautifulSoup,SoupStrainer
import requests
import sys
from bs4.element import Comment
from dateutil.parser import parse
from trash import isTrash
import datetime
import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import faster_than_requests as request

<<<<<<< HEAD
# load data
datadir = '/Capstone_data'
=======

# load data
datadir = 'data'
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
data = pd.read_stata(datadir+"/all_deals.dta")

# drop duplicates
df_unique = data.drop_duplicates(["portfoliocompanyid"],keep="first")

<<<<<<< HEAD
=======

>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
# functions

def hold_your_horses(seconds=5):
    time.sleep(seconds)


<<<<<<< HEAD
def target_date(website,year):
=======
def target_date(website_v,year_v):
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    """
    Will reuturn the first timestamp from
    the specified year
    """
    # I changed this function to return the first available snapshot timestamp
    try:
        hold_your_horses()
<<<<<<< HEAD
        r = requests.get("https://web.archive.org/__wb/calendarcaptures?url="+website+"&selected_year="+str(year),timeout=5).json()
        print(r) ###
=======
        r = requests.get("https://web.archive.org/__wb/calendarcaptures?url="+website_v+"&selected_year="+str(year_v),timeout=5).json()
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
        for m in range(12):
            for w in range(4):
                for t in range(7):
                    value = r[m][w][t]
                    if value is None:
                        continue
                    if 'ts' in value.keys():
                        timestamp = value['ts'][0]
                        if timestamp is not None:
                            return timestamp
                    else:
                        continue
            # except:
            # 	return None
        return None
<<<<<<< HEAD
    except:
        print(f"error target_date: ({website},{year})")
=======
    except :
        error_msg = sys.exc_info()[1]
        log_error("target_date", error_msg)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
        return None



def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'header', 'footer', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def remove_header_and_footer(soup):
    for e in soup.findAll("div", {"class": ["headers", "header", "footer", "footers"]}):
        e.extract()


def text_from_html(soup):  # take in a bs object, not just the link name, need process before hand

    # I added this function to remove header and footer from the html
    remove_header_and_footer(soup)

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    raw = u" ".join(t.strip() for t in visible_texts)
    return str(raw.replace('\t', ' ').replace('\\n', ' ').replace('\n', ' ').strip().encode('ascii', 'ignore'))

def page2text(soup):
    ##Function for scrape text from html
    #try:
    content = text_from_html(soup)
<<<<<<< HEAD
    if len(content)<1000 or content is None or isTrash(content):
=======
    if content is None or isTrash(content):
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
        return ""
    else:
        return content


def homePage(url,timestamp):
    if timestamp is None:
<<<<<<< HEAD
        return None
    url = "https://web.archive.org/web/"+str(timestamp)+"/"+url+"/"
    print(url)
=======
        return None, None
    url = "https://web.archive.org/web/"+str(timestamp)+"/"+url+"/"
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    soup = getSoup(url)
    return soup,url

def getSoup(url):
    try:
        hold_your_horses()
        resp = requests.get(url,timeout=10) # originally, timeout = 3, which may cause the occasionally error in request
        return BeautifulSoup(resp.content, 'html.parser')
    except:
<<<<<<< HEAD
        print(f"error get_soup: ({url})")
        return None


def findPages(website, soup, timestamp):
    toFetch = soup.find_all('a', href=True)
    toFetch = [link for link in toFetch if checkLink(link, website)]
=======
        error_msg = sys.exc_info()[1]
        log_error("getSoup", error_msg)
        return None


def findPages(website_v, soup, timestamp):
    toFetch = soup.find_all('a', href=True)
    toFetch = [link for link in toFetch if checkLink(link, website_v)]
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6

    return [getFullLink(link) for link in toFetch if checkDate(link, str(timestamp))]



<<<<<<< HEAD
def checkLink(href, website):
    # I added this function to remove links that are not useful (only keep link that belongs to the same website)
    href = href["href"]
    invalid_href = ["#"]
    return (href not in invalid_href) and (website in href)
=======
def checkLink(href, website_v):
    # I added this function to remove links that are not useful (only keep link that belongs to the same website)
    href = href["href"]
    invalid_href = ["#"]
    return (href not in invalid_href) and (website_v in href)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6


def checkDate(href, timestamp):
    href = href['href']
    try:
        linkTime = href[href.find('/web/') + 5:href.find('/web/') + 5 + 14]
        ogTime = datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        linkTime = datetime.datetime.strptime(linkTime, "%Y%m%d%H%M%S")
        if abs((linkTime - ogTime).days) < 365:
            return True
        else:
            return False
    except:
<<<<<<< HEAD
        print(f"error checkDate: ({href},{timestamp})")
=======
        error_msg = sys.exc_info()[1]
        log_error("checkDate", error_msg)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
        return False


def getFullLink(href):
    href = href['href']
    if href.startswith('http') or href.startswith('https'):
        return href
    else:
        return "https://web.archive.org" + href


<<<<<<< HEAD
def add_to_visited(visited, url, website):
    where_is = url.find(website)
    before = url[:where_is]
    after = url[where_is + len(website):]
=======
def add_to_visited(visited, url, website_v):
    where_is = url.find(website_v)
    before = url[:where_is]
    after = url[where_is + len(website_v):]
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6

    if before.endswith("http://"):
        before = before[:-7]

    if before.endswith("https://"):
        before = before[:-8]

<<<<<<< HEAD
    visited.append(before + website + after)
    visited.append(before + "http://" + website + after)
    visited.append(before + "https://" + website + after)
=======
    visited.append(before + website_v + after)
    visited.append(before + "http://" + website_v + after)
    visited.append(before + "https://" + website_v + after)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6

    # question: but why do we need these three forms of links?
    # answer: to avoid the case of different url but actually the same domain

    return visited

<<<<<<< HEAD
def add_to_visited2(visited, url, website):
=======
def add_to_visited2(visited, url, website_v):
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    '''
    this new version of visited, only keep the page domain as an "id"
    and get rid of the time machine part in the real domain stored in time machine
    '''
<<<<<<< HEAD
    where_is = url.find(website)
    after = url[where_is+len(website):]
    visited.append(website+after)

    return visited

def getdomain(page,website):
  where_is = page.find(website)
  after = page[where_is+len(website):]
  return website+after


def getText(website, year):
    # this is the homepage object
    print(website, year)
    visited = []
    timestamp = target_date(website, year)
    soup, home_page_url = homePage(website, timestamp)

    if soup is None:  # should we break the function from here?
        return None

    visited = add_to_visited2(visited, home_page_url, website)

    # this is the list of links from the homepage
    toFetch = findPages(website, soup, timestamp)
=======
    where_is = url.find(website_v)
    after = url[where_is+len(website_v):]
    visited.append(website_v+after)

    return visited

def getdomain(page,website_v):
    where_is = page.find(website_v)
    after = page[where_is+len(website_v):]
    return website_v+after


def getText(website_v, year_v):
    # this is the homepage object
    print(website_v, year_v)
    visited = []
    timestamp = target_date(website_v, year_v)
    soup, home_page_url = homePage(website_v, timestamp)

    if soup is None:  # should we break the function from here?
        log_error("soup is None")
        return None

    visited = add_to_visited2(visited, home_page_url, website_v)

    # this is the list of links from the homepage
    toFetch = findPages(website_v, soup, timestamp)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    # this is the text form the homepage
    # at least we will have information form the homepage
    text = page2text(soup)

    # to check duplicated
    text_list = []  # This is new
    text_list.append(text)  # This is also new
    # looping links and get texts
    for page in toFetch:  ###
        # the if prevents re-entering the link
        # (!!but we find that some page links inside the homepage actually
        # have the same domain but different timestep -> this if sentence is not effective)
<<<<<<< HEAD
        if getdomain(page, website) not in visited:
=======
        if getdomain(page, website_v) not in visited:
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6

            soup = getSoup(page)
            if soup is None:
                continue
            text_list.append(page2text(soup)) #Store in list
<<<<<<< HEAD
            visited = add_to_visited2(visited, page, website)
=======
            visited = add_to_visited2(visited, page, website_v)
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6

    text_list = list(dict.fromkeys(text_list))  # Eliminate duplicates
    text = ' ***///*** '.join(text_list)  # Store in text
    print(f"Visited {len(visited)} links")
<<<<<<< HEAD
    print(visited)  ###
=======
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    text = text.strip()
    # wangzhi: to check the duplicated content among all abstracted text from all links
    if len(text) > 50:  # 1000:
        return text
    else:
<<<<<<< HEAD
        return None

def record_startup(cid, year, content):
    filename = path + "/" + str(cid) + "_" + str(year) + '.txt'
=======
        log_error("Text is to short")
        return None

def record_startup(cid, year_v, content):
    filename = path + "/" + str(cid) + "_" + str(year_v) + '.txt'
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    save(filename, content)


def save(filename, content):
    f = open(filename, "w+")
    f.write(content)
    f.close()


<<<<<<< HEAD
=======

# log functions
def initialize_log():
    log = pd.DataFrame({"id":[],"website":[],"year":[],"timestamp":[],"error":[],"detailed_error":[]})
    return log

def log_error(error,detailed_error=""):
    global log, year, website , company_id
    log = log.append({"id":company_id, "website":website,"year":year,"timestamp":datetime.datetime.now(),"error":error,
                      "detailed_error":detailed_error}, ignore_index=True)



>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
path = os.getcwd() + '/data/startup_data'

if not os.path.exists(path):
    os.makedirs(path)

<<<<<<< HEAD
df_startups = df_unique[df_unique.incyear == 2010].iloc[:10]

for index, row in df_startups.iterrows():
    website = row.website
=======
df_startups = df_unique[df_unique.incyear == 2010].iloc[:3]

log = initialize_log()

for index, row in df_startups.iterrows():
    website = row.website
    company_id = row.portfoliocompanyid
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
    year = int(row.incyear) + 1
    text = getText(website, year)
    if text is None:
        continue

    # Save a txt file
    record_startup(row.portfoliocompanyid, year, text)
<<<<<<< HEAD



=======
    
# Log to csv
log.to_csv(path+"/error_log.csv",index=False)
print("Done!")
>>>>>>> 280d005598986c96750351b9cfcd9b4c284932f6
