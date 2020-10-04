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

# load data
datadir = '/data'
data = pd.read_stata(datadir+"/all_deals.dta")

# drop duplicates
df_unique = data.drop_duplicates(["portfoliocompanyid"],keep="first")

# functions

def hold_your_horses(seconds=5):
    time.sleep(seconds)


def target_date(website,year):
    """
    Will reuturn the first timestamp from
    the specified year
    """
    # I changed this function to return the first available snapshot timestamp
    try:
        hold_your_horses()
        r = requests.get("https://web.archive.org/__wb/calendarcaptures?url="+website+"&selected_year="+str(year),timeout=5).json()
        print(r) ###
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
    except:
        print(f"error target_date: ({website},{year})")
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
    if len(content)<1000 or content is None or isTrash(content):
        return ""
    else:
        return content


def homePage(url,timestamp):
    if timestamp is None:
        return None
    url = "https://web.archive.org/web/"+str(timestamp)+"/"+url+"/"
    print(url)
    soup = getSoup(url)
    return soup,url

def getSoup(url):
    try:
        hold_your_horses()
        resp = requests.get(url,timeout=10) # originally, timeout = 3, which may cause the occasionally error in request
        return BeautifulSoup(resp.content, 'html.parser')
    except:
        print(f"error get_soup: ({url})")
        return None


def findPages(website, soup, timestamp):
    toFetch = soup.find_all('a', href=True)
    toFetch = [link for link in toFetch if checkLink(link, website)]

    return [getFullLink(link) for link in toFetch if checkDate(link, str(timestamp))]



def checkLink(href, website):
    # I added this function to remove links that are not useful (only keep link that belongs to the same website)
    href = href["href"]
    invalid_href = ["#"]
    return (href not in invalid_href) and (website in href)


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
        print(f"error checkDate: ({href},{timestamp})")
        return False


def getFullLink(href):
    href = href['href']
    if href.startswith('http') or href.startswith('https'):
        return href
    else:
        return "https://web.archive.org" + href


def add_to_visited(visited, url, website):
    where_is = url.find(website)
    before = url[:where_is]
    after = url[where_is + len(website):]

    if before.endswith("http://"):
        before = before[:-7]

    if before.endswith("https://"):
        before = before[:-8]

    visited.append(before + website + after)
    visited.append(before + "http://" + website + after)
    visited.append(before + "https://" + website + after)

    # question: but why do we need these three forms of links?
    # answer: to avoid the case of different url but actually the same domain

    return visited

def add_to_visited2(visited, url, website):
    '''
    this new version of visited, only keep the page domain as an "id"
    and get rid of the time machine part in the real domain stored in time machine
    '''
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
        if getdomain(page, website) not in visited:

            soup = getSoup(page)
            if soup is None:
                continue
            text_list.append(page2text(soup)) #Store in list
            visited = add_to_visited2(visited, page, website)

    text_list = list(dict.fromkeys(text_list))  # Eliminate duplicates
    text = ' ***///*** '.join(text_list)  # Store in text
    print(f"Visited {len(visited)} links")
    print(visited)  ###
    text = text.strip()
    # wangzhi: to check the duplicated content among all abstracted text from all links
    if len(text) > 50:  # 1000:
        return text
    else:
        return None

def record_startup(cid, year, content):
    filename = path + "/" + str(cid) + "_" + str(year) + '.txt'
    save(filename, content)


def save(filename, content):
    f = open(filename, "w+")
    f.write(content)
    f.close()


path = os.getcwd() + '/data/startup_data'

if not os.path.exists(path):
    os.makedirs(path)

df_startups = df_unique[df_unique.incyear == 2010].iloc[:10]

for index, row in df_startups.iterrows():
    website = row.website
    year = int(row.incyear) + 1
    text = getText(website, year)
    if text is None:
        continue

    # Save a txt file
    record_startup(row.portfoliocompanyid, year, text)



