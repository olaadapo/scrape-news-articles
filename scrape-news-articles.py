# --optional, to let web admin reach out if they want to
# headers = {
#     'User-Agent': 'Morgan, asking@mail.com',
#     'From': 'asking@mail.com'
# }

import requests
from bs4 import BeautifulSoup

# from selenium import webdriver
import time

import pandas as pd
import numpy as np
from datetime import datetime

page = requests.get('https://qz.com/africa/latest')

soup = BeautifulSoup(page.content, 'html.parser')
weblinks = soup.find_all('article')

pagelinks = []
for link in weblinks[5:]:
    url = link.contents[0].find_all('a')[0]
    pagelinks.append('http://qz.com'+url.get('href'))

authorname = []
title = []
thearticle = []
for link in pagelinks:    
    # store the text for each article
    paragraphtext = []    
    # get url
    url = link
    # get page text
    page = requests.get(url)
    # parse with BFS
    soup = BeautifulSoup(page.text, 'html.parser')    
    # get author name, if there's a named author
    try:
        abody = soup.find(class_='d3284 africa').find('a')
        aname = abody.get_text() 
    except:
        aname = 'Anonymous'    

    # get article title
    atitle = soup.find(class_="_21349 africa none _4ca8e")
    thetitle = atitle.get_text() 
    # get main article page
    articlebody = soup.find(class_='_61c55')
    # get text
    articletext = soup.find_all('p')[8:]
    # print text
    for paragraph in articletext[:-1]:
        # get the text only
        text = paragraph.get_text()
        paragraphtext.append(text)        
    # combine all paragraphs into an article
    thearticle.append(paragraphtext)
    authorname.append(aname)
    title.append(thetitle)

# join paragraphs to re-create the article
myarticle = [' '.join(article) for article in thearticle]

# save article data to file
data = {'Title':title, 
        'Author':authorname, 
        'PageLink':pagelinks, 
        'Article':myarticle, 
        'Date':datetime.now()}

oldnews = pd.read_excel('quartz\\news.xlsx')
news = pd.DataFrame(data=data)
cols = ['Title', 'Author', 'PageLink', 'Article', 'Date']
news = news[cols]

afronews = oldnews.append(news)
afronews.drop_duplicates(subset='Title', keep='last', inplace=True)
afronews.reset_index(inplace=True)
afronews.drop(labels='index', axis=1, inplace=True)

filename = 'quartz\\news.xlsx'
wks_name = 'Data'

writer = pd.ExcelWriter(filename)
afronews.to_excel(writer, wks_name, index=False)

writer.save()
