from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
# from sum import news_gathering, process_all_texts,summary_mobilebert,fetch_news
from extrafunc import timed_run,printdebug,load_news_data
from db import get_newslist_for_ai
from index import index
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
newsjson_path = os.path.join(script_dir, "news.json")
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload

@app.get("/")
def home():
    return "home"
# Async queue and lock
update_queue = asyncio.Queue()
update_lock = asyncio.Lock()

# Simulate heavy task


# Worker that processes queue
async def queue_worker():
    while True:
        request, responder = await update_queue.get()
        async with update_lock:
            await index()
            responder.set_result("Update finished.")
        update_queue.task_done()

# Start background worker
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(queue_worker())

# GET endpoint queues the update task
@app.get("/updatenews982")
async def update_endpoint(request: Request):
    responder = asyncio.get_event_loop().create_future()
    await update_queue.put((request, responder))
    result = await responder
    return {"message": result}
@app.get("/updatenews981")
async def shorts(code:str="update"):
    if(code=="update"):
        await index()
        
    return "END OF UPDATE"


# @app.get("/getsummary/")
# def getsummary(txt:str|None = None,url:str | None = None):
#     if txt:
#         return summary_mobilebert(txt)
#     if url:
#         news = fetch_news(url)
        
#         return summary_mobilebert(news)
#     else:
#         return "error"

# @app.get("/ai")
# async def runAI():
#     newsList = get_newslist_for_ai()
#     if newsList:
#         printdebug("in /ai")
#         await process_all_texts(newsList[1:3])
#     return "ai news shorts"

# @app.get("/initial")
# def initial_operations():
#     news_gathering()
#     return "success"

def res():
    return load_news_data(newsjson_path)
    
   
   

# @app.get("/")
# async def root():
#     return short.fetch_html_sourceIE()
    

@app.get("/news")
async def root():
    
    return res() 
#This function is loading news data from news.json and sending as response.
#File news.json is updated with latest news in a different func.

# @app.get("/inshorts")
# async def shorts(count:int=50,category:str="all"):
#     print("get for inshorts")
#     return "inShort.getNews(category,count)"







@app.get("/test")
def test():
  print("CRON JOBB")
  return "hit"
  