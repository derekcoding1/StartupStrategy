#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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
datadir = 'data'
data = pd.read_stata(datadir+"/all_deals.dta")

# drop duplicates
df_unique = data.drop_duplicates(["portfoliocompanyid"],keep="first")


# functions

def hold_your_horses(seconds=5):
    time.sleep(seconds)


def target_date(website_v,year_v):
    """
    Will reuturn the first timestamp from
    the specified year
    """
    # I changed this function to return the first available snapshot timestamp
    try:
        hold_your_horses()
        r = requests.get("https://web.archive.org/__wb/calendarcaptures?url="+website_v+"&selected_year="+str(year_v),timeout=5).json()
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
    except :
        error_msg = sys.exc_info()[1]
        log_error("target_date", error_msg)
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
    if content is None or isTrash(content):
        return ""
    else:
        return content


def homePage(url,timestamp):
    if timestamp is None:
        return None, None
    url = "https://web.archive.org/web/"+str(timestamp)+"/"+url+"/"
    soup = getSoup(url)
    return soup,url

def getSoup(url):
    try:
        hold_your_horses()
        resp = requests.get(url,timeout=10) # originally, timeout = 3, which may cause the occasionally error in request
        return BeautifulSoup(resp.content, 'html.parser')
    except:
        error_msg = sys.exc_info()[1]
        log_error("getSoup", error_msg)
        return None


def findPages(website_v, soup, timestamp):
    toFetch = soup.find_all('a', href=True)
    toFetch = [link for link in toFetch if checkLink(link, website_v)]

    return [getFullLink(link) for link in toFetch if checkDate(link, str(timestamp))]



def checkLink(href, website_v):
    # I added this function to remove links that are not useful (only keep link that belongs to the same website)
    href = href["href"]
    invalid_href = ["#"]
    return (href not in invalid_href) and (website_v in href)


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
        error_msg = sys.exc_info()[1]
        log_error("checkDate", error_msg)
        return False


def getFullLink(href):
    href = href['href']
    if href.startswith('http') or href.startswith('https'):
        return href
    else:
        return "https://web.archive.org" + href


def add_to_visited(visited, url, website_v):
    where_is = url.find(website_v)
    before = url[:where_is]
    after = url[where_is + len(website_v):]

    if before.endswith("http://"):
        before = before[:-7]

    if before.endswith("https://"):
        before = before[:-8]

    visited.append(before + website_v + after)
    visited.append(before + "http://" + website_v + after)
    visited.append(before + "https://" + website_v + after)

    # question: but why do we need these three forms of links?
    # answer: to avoid the case of different url but actually the same domain

    return visited

def add_to_visited2(visited, url, website_v):
    '''
    this new version of visited, only keep the page domain as an "id"
    and get rid of the time machine part in the real domain stored in time machine
    '''
    where_is = url.find(website_v)
    after = url[where_is+len(website_v):]
    visited.append(website_v+after)

    return visited

def getdomain(page,website_v):
    where_is = page.find(website_v)
    after = page[where_is+len(website_v):]
    return website_v+after


def getText(website_v, year_v, company_id): #nclude Id of company to include this in the output data, that is going to be a dict
    # this is the homepage object
    print(website_v, year_v)
    visited = []
    timestamp = target_date(website_v, year_v)
    soup, home_page_url = homePage(website_v, timestamp)

    if soup is None:  # should we break the function from here?
        log_error("soup is None")
        return None, None

    visited = add_to_visited2(visited, home_page_url, website_v)

    # this is the list of links from the homepage
    toFetch = findPages(website_v, soup, timestamp)
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
        
        if getdomain(page, website_v) not in visited:

            soup = getSoup(page)
            
            if soup is None:
                continue
                
            text_list.append(page2text(soup)) #Store in list
            
            visited = add_to_visited2(visited, page, website_v)
            
            
    ID = [company_id]*len(visited)
    YR = [year_v]*len(visited)
    lastpath = [os.path.basename(x) for x in visited]
    
    
    dict_text = {'ID': ID ,'Year': YR, 'Visited_link': visited,'Name_Path':lastpath , 'Text': text_list}

    #text_list =   # We deactivate this function to keep track of the links visited
                 
    text = ' ***///*** '.join(list(dict.fromkeys(text_list)))  # Store in text only non reapeted text
    
    print(f"Visited {len(visited)} links")
    
    text = text.strip()
       
    # wangzhi: to check the duplicated content among all abstracted text from all links
    if len(text) > 50:  # 1000:
        return text , dict_text
    else:
        log_error("Text is to short")
        return None, None

    
           
def record_startup(cid, year_v, content):
    filename = path + "/" + str(cid) + "_" + str(year_v) + '.txt'
    save(filename, content)


def save(filename, content):
    f = open(filename, "w+")
    f.write(content)
    f.close()



# log functions
def initialize_log():
    log = pd.DataFrame({"id":[],"website":[],"year":[],"timestamp":[],"error":[],"detailed_error":[]})
    return log

def log_error(error,detailed_error=""):
    global log, year, website , company_id
    log = log.append({"id":company_id, "website":website,"year":year,"timestamp": datetime.datetime.now(),"error":error,
                      "detailed_error":detailed_error}, ignore_index=True)
    
    
#################


path = os.getcwd() + '/data/startup_data'

if not os.path.exists(path):
    os.makedirs(path)

df_startups = df_unique[df_unique.incyear == 2010].iloc[0:4] # change for the hole year
log = initialize_log()

dict_ini = {'ID': [],'Year': [], 'Visited_link': [], 'Name_Path':[], 'Text': []}

text_data_frame = pd.DataFrame(dict_ini)
text_data_frame.to_csv(path+'/Text_data_frame.csv', index=False)


for index, row in df_startups.iterrows():
    website = row.website
    company_id = row.portfoliocompanyid
    year = int(row.incyear) + 1
    text, dict_data_frame = getText(website, year, company_id) #Include the output dataframe
             
    if text is None:
        continue
        
    comp_dataframe = pd.DataFrame.from_dict(dict_data_frame)
    
    comp_dataframe.to_csv(path+"/Text_data_frame.csv",mode = 'a',index = False, header= False)
    
    del comp_dataframe

    # Save a txt file
    record_startup(row.portfoliocompanyid, year, text)
    
# Log to csv
log.to_csv(path+"/error_log.csv",index=False)

print("Done!")

    

