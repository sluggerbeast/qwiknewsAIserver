import aiohttp
import asyncio
from newspaper import Article,fulltext
from extrafunc import news_data, writeNewsToJsonFile,load_news_data
from extrafunc import cat as category, timed_run,printdebug
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
#fetch_content fetches and parses html data to get clean news in async
import random
import time

# Limit concurrent connections
MAX_CONCURRENT_REQUESTS = 1
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# List of real browser user-agents (rotate to avoid blocks)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

async def fetch_content(session, url, retries=3):
    async with semaphore:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com"
        }

        for attempt in range(retries):
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        # print(f"[{response.status}] Fetched: {url}")
                        return await fulltext(response.text())
                    else:
                        print(f"[{response.status}] Failed: {url}")
            except asyncio.TimeoutError:
                print(f"[Timeout] {url}")
            except aiohttp.ClientConnectorError as e:
                print(f"[Connection Error] {url}: {e}")
            except Exception as e:
                print(f"[Error] {url}: {e}")

            await asyncio.sleep(1 + random.random())  # small random delay before retry

        print(f"[Failed after {retries} retries] {url}")
        return None

async def main(urlList):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session,news["url"]) for news in urlList]
        fullnews_list = await asyncio.gather(*tasks)
        # printdebug(fullnews_list[1][:30])
        for news,fullnews in zip(urlList,fullnews_list):
            news["fullnews"] = fullnews
        # var = load_news_data("news.json")
        # writeNewsToJsonFile({"data": {
        # "category_list":category,
        # "news_list": urlList
        # }})
        return urlList

@timed_run
async def newsContentGathering(urlList):
    
   return await main(urlList)