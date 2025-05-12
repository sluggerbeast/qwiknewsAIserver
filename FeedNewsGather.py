from datetime import datetime
import json
import uuid
import feedparser as fp
import re
from tqdm import tqdm

all_hindu_feeds = "https://www.thehindu.com/rssfeeds/"
all_firstpost_feeds = "https://www.firstpost.com/rss/"
all_newyorktimes_feeds = "https://www.nytimes.com/rss"
all_dainikbhaskar_feeds = "https://www.bhaskar.com/rss"



category_urls={    
    "business":["https://www.thehindu.com/business/feeder/default.rss",15],
    "sports": ["https://www.thehindu.com/sport/feeder/default.rss",10],
    "entertainment":["https://indianexpress.com/section/entertainment/feed/",5],
    "india" : ["https://www.thehindu.com/news/national/feeder/default.rss",15],
    "world" : ["https://www.firstpost.com/commonfeeds/v1/mfp/rss/world.xml",15],
    "technology" : ["https://www.firstpost.com/commonfeeds/v1/mfp/rss/tech.xml",10],
    "education": ["https://health.economictimes.indiatimes.com/rss/education",5],
    "health": ["https://www.thehindu.com/life-and-style/fitness/feeder/default.rss",5]
    
    }
'''
{
                'id': uuid.uuid4().hex,
                'title': title_element.text.strip(),
                'description': content,
                "fullnews":"",
                'urlToImage': img_url,
                "url": page_url,
                "category": extractCat(page_url),
                "date":date.split(",")[0],
            }
'''

categories = ["business","sports","india","world","technology","education","entertainment","health"]
placeholder_image= "https://placehold.co/600x450/333333/FFFFFF?text=Image+Not+Available"
def get_image(entry):
    image_url = None

    # 1. Check media_content
    if 'media_content' in entry:
        image_url = entry.media_content[0]['url']

    # 2. Check media_thumbnail
    elif 'media_thumbnail' in entry:
        image_url = entry.media_thumbnail[0]['url']

    # 3. Check for <img> tag in summary
    elif 'summary' in entry:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if match:
            image_url = match.group(1)

    # 4. Check enclosures
    elif 'enclosures' in entry and len(entry.enclosures) > 0:
        image_url = entry.enclosures[0].get('href')
    return image_url
def structure_news(feed, newsCount,category):
    temparray = []
    entries = feed.entries[:int(newsCount)]
    for news in entries:
        # print(type(news.description))
        temparray.append({
            "id":uuid.uuid4().hex,
            "title":news.title,
            "description":news.summary if news.summary else news.description,
            "fullnews":"",
            "urlToImage": get_image(news) if get_image(news) else placeholder_image,
            "url":news.link,
            "category":category,
            "date":datetime(*news.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S") if news.published_parsed else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    print(len(temparray))
    return temparray

def get_news():
    newsList = []
    for category in tqdm(categories,"fetching news"):
        news_feed = fp.parse(category_urls[category][0])
        temp = structure_news(news_feed,category_urls[category][1],category)
        newsList.extend(temp)
    # print(json.dumps(newsList, indent=4))
    return newsList
    

if __name__=="__main__":
    print(len(get_news()))



