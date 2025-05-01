from datetime import datetime
import sqlite3
import requests
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "news.db")
from extrafunc import cat , summary_flag

from extrafunc import timed_run, printdebug,writeNewsToJsonFile

newsList = []

# {
#                 'id': uuid.uuid4().hex,
#                 'title': title_element.text.strip(),
#                 'description': content,
#                 'urlToImage': img_url,
#                 "url": page_url,
#                 "fullnews":"xyz",
#                 "category": extractCat(page_url),
#                 "date":date.split(",")[0],
#             }

#First step to create a database and connect, it it doesn't exist, it creates one.
def Initial_db_operation(arr):
    
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    # Creates table and its columns
    create_entries(connection,cursor) 
    printdebug("database connected")
    # adds initial news data(without the complete news) to db
    insert_data(connection,cursor,arr)
    printdebug("inserted initial news data in db")
    connection.commit()
    connection.close()
    printdebug("Basic db operation complete")
    # return vari


def create_entries(connection,cursor):
    
    create_table_queries = '''
                            CREATE TABLE IF NOT EXISTS news (
                            id text primary key unique,
                            title text,
                            description text,
                            urltoimg text,
                            url text unique,
                            fullnews text,
                            category text,
                            date text
                            );

                            '''
    cursor.execute(create_table_queries)
    # cursor.execute("DELETE FROM NEWS")
    connection.commit()
    printdebug("table exists/created")
def insert_data(connection,cursor,arr):
    
    
    for news in arr:
        cursor.execute("INSERT OR REPLACE INTO news (ID,TITLE,DESCRIPTION,URLTOIMG,URL,FULLNEWS,CATEGORY,DATE) VALUES (?,?,?,?,?,?,?,?)", ( 
                        news["id"],
                        news["title"],
                        news["description"],
                        news["urlToImage"],
                        news["url"],
                        news["fullnews"],
                        news["category"],
                        news["date"],
                        
                           ))
        
        connection.commit()
@timed_run
def get_newslist_for_ai():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute( "SELECT fullnews, id FROM NEWS")
    arr = cursor.fetchall()
    connection.close()
    return arr
    
    # arr = []
    # for row in urls:
    #     printdebug(row[0])
    
    
    
#accepts a list of tuples (description,id)
@timed_run
def update_summary(NewsList):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    printdebug("nside updating summaryI")
    query = "UPDATE NEWS SET DESCRIPTION = ? WHERE ID = ?"
    cursor.executemany(query,NewsList)
    connection.commit()
    connection.close()       
    
        
    printdebug("all news summary added")
def date_to_words(date_str):
    # print(date_str)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d %Y")  # e.g., "May 01, 2025"
    except Exception as e:
        print(f"Date conversion failed: {e}")
        return date_str

def db_to_json():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = "SELECT * FROM NEWS order by date desc limit 100"
    cursor.execute(query)
    news = cursor.fetchall()
    # cursor.execute("select distinct category from news")
    # cat = cursor.fetchall()
    connection.close
    newsList = []
    summary_flag = True
    print(summary_flag)
    if(summary_flag):
        for arr in news:
            newsList.append({
                'id':arr[0],
                'title': arr[1],
                'description': arr[2],                
                'urlToImage': arr[3],
                "url": arr[4],
                
                "category": arr[6],
                "date":date_to_words(arr[7]),
            })
    if(len(newsList)>0):
        print(len(newsList))
        writeNewsToJsonFile({"data": {"category_list":cat,"news_list": newsList}})
    summary_flag = False

def check_duplicate(obj):
    # print("checking duplicate")
    Connection = sqlite3.connect(db_path)
    cursor = Connection.cursor()
    
    cursor.execute("SELECT URL FROM NEWS WHERE URL = ?",(obj["url"],))
    val = cursor.fetchone()
    # print(val[0])
    if val is None:
            return False 
    if(val[0]):
        return True
    else:
        return False
    

if __name__ == "__main__":
    # get_newslist_for_ai()
    summary_flag = True
    db_to_json()
# create_connection()

