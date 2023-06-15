import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from langchain.document_loaders import DirectoryLoader
import nest_asyncio
from langchain.document_loaders import WebBaseLoader
nest_asyncio.apply()
import os
import asyncio
import aiohttp
import tiktoken
from dotenv import load_dotenv
import time
from utils import extract_unique_absolute_urls, download_html_pages

def main():
    load_dotenv()
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    # os.environ['ACTIVELOOP_TOKEN'] = os.getenv('ACTIVELOOP_TOKEN')

    api_doc_url = input('Enter the API documentation Link: ')
    
    max_attempts = int(os.getenv('MAX_ATTEMPTS', 5)) 


    for attempt in range(1, max_attempts+1):
        try:
            print('Scraping the Documentation...\n')
            start_time = time.time()  
            absolute_urls = extract_unique_absolute_urls(url=api_doc_url)
            elapsed_time = time.time() - start_time  
            print(f"Time needed to pull the data: {elapsed_time:.2f}s.")
            break  
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt == max_attempts:
                print("Max attempts reached. Exiting...")
                return
            else:
                print("Retrying...")


if __name__ == "__main__":
    main()