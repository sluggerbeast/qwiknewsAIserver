'''
    Scrape first level of data in asynchronous mode
    then immediately scrape the full news content using newspaper3k library
    the sequenial summary generation

    Use aiohttp + asyncio to fetch HTMLs fast.
→ Parse immediately with BeautifulSoup.
→ Control concurrency with a semaphore if needed.
    
'''
import asyncio
import requests
from bs4 import BeautifulSoup
import uuid
import time
import json
from newsGathering import filter_duplicates #,get_news,
from newsContentGathering import newsContentGathering
from FeedNewsGather import get_news
from db import Initial_db_operation,db_to_json
from summarize import runAI
from newspaper import fulltext
from extrafunc import news_data
from tqdm import tqdm

def temp_fullnews(newsList):
    for news in tqdm(newsList,"getting full news"):
      html = requests.get(news["url"]).text
      news["fullnews"] = fulltext(html)
    return newsList

def qualitycontrol(newsList):
    defective_array = []
    good_array = []
    for news in newsList:
       temp = news["description"]
       if(len(temp.split())<40):
          defective_array.append(news)
       else:
          good_array.append(news)
    
   
async def index():
    #Step 1 to curate news and extract basic info
    # new_data_initial = await get_news() #returns an array with selected news and its data
    # new_data_initial = requests.get("https://qwiknewsbackend.onrender.com/newsapi").json()["data"]["news_list"]
    new_data_initial = []
    
    new_data_initial = get_news()
    #step 2 from the basic info extract news article for summary
        
    print(len(new_data_initial))
    filtered_newslist  = filter_duplicates(new_data_initial)
    # news_with_fullnews = await newsContentGathering(new_data_initial)
    if(len(filtered_newslist)==0):
       print("no new news")
       return
    news_with_fullnews = temp_fullnews(filtered_newslist)
    # #step 3 adding the news data with fulltext into db
   # this step to quality control news article, remove or resummarize

    

    ##########################################
    Initial_db_operation(news_with_fullnews)
    # #step 4 summarizing the full article to around 60 words and putting back into database
    runAI(news_with_fullnews)
    # news_with_fullnews = qualitycontrol(news_with_fullnews)
    db_to_json()

if __name__ =="__main__":
  asyncio.run(index())