import time
import torch
import json
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
newsjson_path = os.path.join(script_dir, "news.json")

summary_flag = False
news_data = []
ENV = "dev"
debugFlag = True if ENV=="dev" else False
cat = [
   "political-pulse",
   "sports",
   "business",
   "technology",
    "education"]
###########--------functions from here----------######
def printdebug(val):
    if debugFlag is True:
        print(val)

# get the run time of a function
def timed_run(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        printdebug(f"Function '{func.__name__}' executed in {execution_time:.2f} seconds")
        return result
    return wrapper
@timed_run
def writeNewsToJsonFile(jsonfile):
       
    # Open the file in write mode ("w")
    with open(newsjson_path, "w") as outfile:
        # Write the JSON data to the file using json.dump()
        json.dump(jsonfile, outfile, indent=2)  
        # Add indentation for readability (optional)
def load_news_data(filename=newsjson_path):
  """
  Loads news data from a JSON file.

  Args:
      filename (str): The path to the JSON file containing news data.

  Returns:
      dict: A dictionary containing the loaded news data, 
            or None if an error occurs.
  """
  try:
    # Open the JSON file in read mode
    with open(filename, 'r') as file:
      # Load the JSON data into a dictionary
      data = json.load(file)
      print(type(data))
    return data
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    return None
  except json.JSONDecodeError as e:
    print(f"Error: Failed to parse JSON data. {e}")
    return None