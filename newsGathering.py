import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import uuid
import time
import random
import json
from db import check_duplicate
from extrafunc import news_data,timed_run,printdebug, writeNewsToJsonFile
from extrafunc import cat
category = "category"
keywords = "keywords"
IEurl= "https://indianexpress.com/section/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

categoryList = [
  { id: 1, category: "political-pulse", keywords: ["politics", "bjp", "congress", "voting", "election",
"cities","national","political-pulse","india"] },

  { id: 2, category: "sports", keywords: ["sports", "ipl", "footbal",] },
  { id: 3, category: "health", keywords: ["health", "lifestyle",] },
  { id: 4, category: "technology/science", keywords: ["technology",] },
  { id: 5, category: "entertainment", keywords: ["entertainment", "celebrity", "actor", "movies"] },
  { id: 6, category: "business", keywords: ["business", "investment", "funding"] },
  { id: 7, category: "", keywords: ["miscellaneous","explained",] },
  { id: 8, category: "education", keywords: ["education", "college", "school"] },
  { id: 9, category: "startup", keywords: ["startup", "investor"] },
  
  { id: 10, category: "lifestyle", keywords: ["travel"] },
  { id: 11, category: "", keywords: ["science"] },
  { id: 12, category: "fashion", keywords: ["fashion", "outfit"] },
  { id: 13, category: "international", keywords: ["international", "world"] },

]

def filter_duplicates(array):
    if array:
        print(len(array), "before")
        filtered = [news for news in array if not check_duplicate(news)]
        print(len(filtered), "after")
        return filtered
    else:
        return array
         


def extractCat(url):
    url_parts = url.split("/")

    # Extract the desired element (assuming "education" is the third element)
    category = url_parts[4]
    return category

def parse_html_for_news(html_content):
    """
    Parses HTML content to extract shorts information.

    Args:
        html_content (str): The HTML content to be parsed.

    Returns:
        list: A list of dictionaries containing extracted information (if successful).
              Empty list if parsing fails.
    """
    if html_content is None:
        print("Warning: Received None HTML, skipping parsing.")
        return
    soup = BeautifulSoup(html_content, 'html.parser')

    # Adjust selectors based on website structure (replace placeholders)
    articles = soup.find_all('div', class_='articles')  # Assuming articles are within 'shorts-card' elements
    
    # print(articles)

    scraped_data = []
    for article in articles:
        
        date = article.find('div',class_='date').text.strip()
        # print(date)
        img_tag = article.find('img')
        if img_tag:
            img_url = img_tag.get("data-src") or img_tag.get("src")
        else:
            img_url = ""
       
        title_element = article.find('h2', class_='title').find('a')
        title_text = ""
        page_url = ""
        
        title_text = title_element.get('title')
        page_url = title_element.get('href')
       
        content_element = article.find("p")
        if(content_element!=None):
           content = content_element.text.strip()
        else:
            content = title_text
        

        if title_element and content_element:
            scraped_data.append({
                'id': uuid.uuid4().hex,
                'title': title_element.text.strip(),
                'description': content,
                "fullnews":"",
                'urlToImage': img_url,
                "url": page_url,
                "category": extractCat(page_url),
                "date":date.split(",")[0],
            })

    
    news_data.extend(scraped_data)
    return scraped_data



  
MAX_CONCURRENT_REQUESTS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

async def fetch_html_source(session, url, retries=3):
    timeout = aiohttp.ClientTimeout(total=10)

    async with semaphore:
        for attempt in range(1, retries + 1):
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com"
                }

                async with session.get(url, timeout=timeout, headers=headers) as response:
                    if response.status == 200:
                        # print(f"[{response.status}] Success: {url}")
                        return await response.text()
                    else:
                        print(f"[{response.status}] Failed: {url}")

            except asyncio.TimeoutError:
                print(f"[Timeout] {url} (Attempt {attempt})")
            except aiohttp.ClientError as e:
                print(f"[ClientError] {url}: {e} (Attempt {attempt})")
            except Exception as e:
                print(f"[Error] {url}: {e} (Attempt {attempt})")

            await asyncio.sleep(2 + random.random())  # polite backoff delay

    print(f"[Failed after {retries} retries] {url}")
    return None
### main function to get and do scraping
@timed_run
async def News_main(category_urls):
    async with aiohttp.ClientSession() as session:
        fetching_tasks = [fetch_html_source(session, url) for url in category_urls]
        responses = await asyncio.gather(*fetching_tasks)

        for html_cont in responses:
            if html_cont:  # Defensive check to avoid passing None
                parse_html_for_news(html_cont)
            else:
                print("[Warning] Skipping parse due to empty content.")

def extractCat(url):
    if(not url):
       return ""
    url_parts = url.split("/")

    # Extract the desired element (assuming "education" is the third element)
    category = url_parts[4]
    return category
   
   
# print(IE_News(IEurl,"entertainment"))
@timed_run
async def get_news():
   
    
    #add IEurl in from of categories for better 
    temp_cat = []
    for i in cat:
       temp_cat.append(IEurl+i)
    
    news_array = []
    
    
    
    
    # writeNewsToJsonFile({"data": {
    # "category_list":cat,
    # "news_list": news_data
    # }})
    # printdebug(news_data[1:2])
    return await News_main(temp_cat)
    # print(len(news_array))

# Print the JSON data
if __name__ == "__main__":
    get_news()
    printdebug(news_data[1:4])
# print(len(news_array))
