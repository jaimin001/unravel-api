import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import WebBaseLoader
import os
import asyncio
import aiohttp
import tiktoken
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
import codecs
from langchain.document_loaders import TextLoader


def tiktoken_length(text):
    tokenizer = tiktoken.get_encoding('cl100k_base')
    return len(tokenizer.encode(text))

def extract_unique_absolute_urls(url, visited_links=None, depth_limit=3, current_depth=0):
    if visited_links is None:
        visited_links = set()

    if current_depth > depth_limit:
        return visited_links

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    absolute_urls = set()
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("http") and not href.startswith("#"):
            absolute_url = urljoin(url, href)
            absolute_url_without_fragment = urldefrag(absolute_url).url
            if absolute_url_without_fragment not in visited_links:
                absolute_urls.add(absolute_url)
                visited_links.add(absolute_url_without_fragment)

    for absolute_url in absolute_urls:
        visited_links = extract_unique_absolute_urls(absolute_url, visited_links, depth_limit, current_depth + 1)

    return visited_links


def save_list_to_file(data_list, file_path):
    with open(file_path, 'w') as file:
        for item in data_list:
            file.write(str(item) + '\n')


async def download_html_page(session, url, folder):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            html_content_bytes = await response.content.read()

            # Extract the file name from the URL
            filename = url.split("/")[-1]

            # Create the folder if it doesn't exist
            os.makedirs(folder, exist_ok=True)

            # Save the HTML content to a file in the specified folder
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, "wb") as file:
                    file.write(html_content_bytes)
            except Exception as e:
                print(f"Error saving file: {str(e)}")
            else:
                print(f"Successfully downloaded HTML from {url} and saved as {filepath}")

    except aiohttp.ClientError as e:
        print(f"Error downloading HTML from {url}: {str(e)}")

def read_txt_file(filename, encoding):
    with codecs.open(filename, "r", encoding=encoding, errors="replace") as file:
        file_text = file.read()
    return encoding, file_text


async def download_html_pages(url_list, folder):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in url_list:
            task = asyncio.ensure_future(download_html_page(session, url, folder))
            tasks.append(task)

        await asyncio.gather(*tasks)

def load_documents(folder_path):
    loader = DirectoryLoader(folder_path, glob="**/*.html", show_progress=True, loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True}, silent_errors=True)
    print("=" * 100)
    print('Loading docs...')
    docs = loader.load()
    print(f"Loaded {len(docs)} documents.")
    return docs


def create_database_for_link(api_doc_url, path, max_attempts=3):
    
    success = False
    for attempt in range(1, max_attempts+1):
        try:
            print('Scraping the Documentation...\n')
            start_time = time.time() 
             
            ## Get all the absolute urls
            print(api_doc_url)
            absolute_urls = extract_unique_absolute_urls(url=api_doc_url, depth_limit=1)
            ## save the absolute urls to a file
            path_to_absolute_urls = f'{path}/absolute_urls.txt'
            save_list_to_file(absolute_urls, path_to_absolute_urls)
            ## Download all the corresponding pages
            path_to_html_pages = f'{path}/files'
            asyncio.run(download_html_pages(absolute_urls, path_to_html_pages))
            
            elapsed_time = time.time() - start_time  
            print(f"Time spent to pull the data: {elapsed_time:.2f}s.")
            success = True
            break  
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt == max_attempts:
                print("Max attempts reached. Exiting...")
                return
            else:
                print("Retrying...")
    return success


def split_documents(docs):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size = 1000,
            chunk_overlap  = 50,
            length_function = len,
            separators=["\n\n", "\n", " ", ""],
        )
        texts = text_splitter.split_documents(docs)
        return texts
    except:
        return False
    
def get_user_input():
    user_query = st.text_input('Enter your query...')
    if user_query.lower() == 'quit':
        return None
    return user_query

def print_answer(question, answer):
    st.write(f"Question: {question}")
    st.write(f"Response: \n {answer}")
