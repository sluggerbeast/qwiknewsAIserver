import requests
import os
import functools
from db import  get_newslist_for_ai,update_summary

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

from transformers import T5Tokenizer, T5ForConditionalGeneration, BartTokenizer, BartForConditionalGeneration
from concurrent.futures import ThreadPoolExecutor
import time
import torch
import asyncio
from extrafunc import printdebug, timed_run, news_data,summary_flag
from newspaper import Article
from extrafunc import load_news_data




# Load model and tokenizer
# -------------flan-t5-base--------------
#device type cpu/cuda, model size: small, base, large
@functools.cache
@timed_run
def load_model(model_choice="flan-t5-small", device="cpu"):
    if device == "gpu":
        device = "cuda"

    if model_choice.startswith("flan"):
        model_name = f"google/{model_choice}"
        tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
        model = T5ForConditionalGeneration.from_pretrained(model_name).to(device)
    elif model_choice == "distilbart":
        model_name = "sshleifer/distilbart-cnn-12-6"
        tokenizer = BartTokenizer.from_pretrained(model_name)
        model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
    else:
        raise ValueError("Model choice must be either 'flan-t5-base' or 'distilbart'")
    
    return tokenizer, model, device

# --------- SUMMARIZATION FUNCTION ---------
def summarize_texts(texts, tokenizer, model, device, model_choice, batch_size=5, summary_word_limit=100):
    if isinstance(texts, str):
        texts = [texts]

    all_summaries = []
    model.eval()

    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        results = executor.map(lambda batch: summarize_batch(batch, tokenizer, model, device, model_choice, summary_word_limit), batches)

        for batch_result in results:
            all_summaries.extend(batch_result)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    return all_summaries

# --------- HELPER FUNCTION ---------
def summarize_batch(batch_texts, tokenizer, model, device, model_choice, summary_word_limit=120):
    if model_choice.startswith("flan"):
        prompts = [
            f"You are a professional news editor. Summarize the text to make it concise, factually accurate, do not omit facts, always complete sentences with fullstop and neutral in tone. Output should reflect journalistic standards. Text: {text}"
            for text in batch_texts
        ]
    else:
        prompts = batch_texts

    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)

    with torch.inference_mode():
        summary_ids = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=summary_word_limit,
            min_length=max(90, int(summary_word_limit*0.8)),
            num_beams=4,
            repetition_penalty=2.5,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

    summaries = tokenizer.batch_decode(summary_ids, skip_special_tokens=True)
    printdebug(summaries)
    return summaries
# --------------flan-t5-base end-----------------------
# @functools.cache
# @timed_run
# def summary_t5_d(text, summary_word_limit=100,dev="cpu",modelSize="base"):
#     if dev=="gpu":
#         dev = "cuda"
    
#     device = torch.device(dev)

#     model_name = f"google/flan-t5-{modelSize}"
#     tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
#     model = T5ForConditionalGeneration.from_pretrained(model_name).to(device)

#     # Add prompt for summarization
#     input_text = f"Extract the complete main news story from the following text in at least 60 words.Keep the summary factual and informative. Text: {text}"
    
#     # #Tokenize and generate summary
#     input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)
#     summary_ids = model.generate(
#         input_ids, 
#         max_length=512, 
#         min_length=256, 
#         length_penalty=1.0, 
#         num_beams=4, 
#         repetition_penalty=2.5,
#         no_repeat_ngram_size=3,
#         early_stopping=True
#     )
#     summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

#     # #Generate title from summary
#     input_text = f"You are a professional news editor. Rewrite the following summary to make it concise, factually accurate, and neutral in tone. Output should reflect journalistic standards. Original Summary: {summary}"
#     title_ids = model.generate(
#         tokenizer.encode(input_text, return_tensors="pt").to(device), 
#         max_length=150, 
#         min_length=100, 
#         num_beams=4, 
#         repetition_penalty=2.5,
#         no_repeat_ngram_size=3,
#         early_stopping=True
#     )
#     title = tokenizer.decode(title_ids[0], skip_special_tokens=True)

#     return f"{title}"
# ---------------Bert model---------
@timed_run
def summary_mobilebert(content):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    summary = summarizer(content, min_length=100, do_sample=False, truncation=True)
    return summary[0]["summary_text"]

#-------------bert model end---------
  
# ------------html retrival end here--------------------

@timed_run
def runAI(newslist):
    summary_flag = False
    # newsL = get_newslist_for_ai()
    newsList = [(x["fullnews"], x["id"]) for x in newslist]
    device = "cpu"
    print(f"len of list {len(newsList)}")
    if(len(newsList)>=30):
        model_choice = "flan-t5-small"
        device = "gpu"
    elif (len(newsList)<30 and len(newsList)>=20):
        model_choice = "flan-t5-base"
        device = "cpu"
    elif (len(newsList)<20):
        model_choice = "distilbart"
        device = "gpu"
    printdebug(F"{model_choice},{device}")
    # #model_choice = "distilbart"
    # model_choice = "flan-t5-small"
    tokenizer, model, device = load_model(model_choice=model_choice, device=device)
    print("model_loaded")
    summaries = summarize_texts(
        texts=[x[0] for x in newsList],  # extracting only the full news texts
        tokenizer=tokenizer,
        model=model,
        device=device,
        model_choice=model_choice,
        batch_size=5
    )
    summary_flag = True if len(summaries)>0 else False
    summary_list = []
    for x,y in zip(summaries,newsList):
        print(x,y[1])
        summary_list.append((x,y[1]))
    update_summary(summary_list)
    

if __name__ == "__main__":
    
    try:
       
        start = time.time()
        
        # news_gathering()
        runAI()
        stop = time.time()
        printdebug(f"total ai time: {stop-start}")
        
        
        # print(time_execution(summary_t5)(news_content))
        
        # print(time_execution(summary_mobilebert)(news_content))
        printdebug("=======all done==================")
        # print(news_content)
        
    except Exception as e:
        print(f"Error: {e}")


# Notes
# flan-t5-base model works really well when use doubled
#"sshleifer/distilbart-cnn-12-6" model is also good but not as good as flan-t5-base