import requests
from bs4 import BeautifulSoup
import uuid
import time
import random
import json
from db import check_duplicate
from extrafunc import timed_run, printdebug, writeNewsToJsonFile
from extrafunc import cat

news_data = []
IEurl = "https://indianexpress.com/section/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def extractCat(url):
    if not url:
        return ""
    url_parts = url.split("/")
    return url_parts[4] if len(url_parts) > 4 else ""
from datetime import datetime

def clean_date(date_parts):
    try:
        
        # Combine and strip unnecessary parts
        val =date_parts.split(",")
        # print(type(dat))
        date_str = val[0]+" "+val[1].strip().split()[0]
        # Convert to datetime object
        date_obj = datetime.strptime(date_str, "%B %d %Y")
        # Format to YYYY-MM-DD
        return date_obj.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Date parsing failed: {e}")
        return None

def parse_html_for_news(html_content):
    if html_content is None:
        print("Warning: Received None HTML, skipping parsing.")
        return
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all('div', class_='articles')

    scraped_data = []
    for article in articles:
        try:
            date = article.find('div', class_='date').text.strip()
            img_tag = article.find('img')
            img_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""

            title_element = article.find('h2', class_='title').find('a')
            title_text = title_element.get('title')
            page_url = title_element.get('href')

            content_element = article.find("p")
            content = content_element.text.strip() if content_element else title_text
            date_var = clean_date(date) if clean_date(date) else date.split(",")[0]
            # print(date_var)
            # print(date)
            if title_element:
                scraped_data.append({
                    'id': uuid.uuid4().hex,
                    'title': title_element.text.strip(),
                    'description': content,
                    "fullnews": "",
                    'urlToImage': img_url,
                    "url": page_url,
                    "category": extractCat(page_url),
                    "date": date_var,
                })
        except Exception as e:
            print(f"Error parsing article: {e}")

    news_data.extend(scraped_data)
    return scraped_data

def fetch_html_source(url, retries=3):
    for attempt in range(1, retries + 1):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com"
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"[{response.status_code}] Failed: {url}")
        except requests.RequestException as e:
            print(f"[RequestError] {url}: {e} (Attempt {attempt})")

        time.sleep(2 + random.random())

    print(f"[Failed after {retries} retries] {url}")
    return None

@timed_run
def News_main(category_urls):
    for url in category_urls:
        html_cont = fetch_html_source(url)
        if html_cont:
            parse_html_for_news(html_cont)
        else:
            print("[Warning] Skipping parse due to empty content.")

@timed_run
def get_news():
    temp_cat = [IEurl + i for i in cat]
    News_main(temp_cat)
    if(news_data[0]):
        return news_data

if __name__ == "__main__":
    get_news()
    printdebug(news_data[1:4])
