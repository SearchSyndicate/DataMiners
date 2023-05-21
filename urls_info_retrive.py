# -*- coding: utf-8 -*-
"""golbal_web_scrapper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jHFnI2_o-aSG8esv31GcFcIY9uSxxZt5

## global web scrapper
"""

import re
import requests
import pandas as pd
import tldextract

GOOGLE_SEARCH_ENGINE_ID =  "c51e2a70bf5174ccc"
GOOGLE_API_KEY = "AIzaSyCJKCZR7VFuRcW6GxmqcNVHJN9OxC1iLr0"

## function to extract info
def domain_extract(url):
    ext = tldextract.extract(url)
    return ext.domain

def get_tag_text(url, page_source_text, tag_text):
    tag_text_list = page_source_text.find_all(tag_text)
    tag_texts = [div.text for div in tag_text_list]
    return list(set(tag_texts))

## public API for duckduckgo
def get_url_from_name(query):
    # Specify your search query

    # Construct the API request URL
    url = f'https://api.duckduckgo.com/?q={query}&format=json'
    # goole API
    
    endpoint = "https://www.googleapis.com/customsearch/v1"

    # Send the API request
    response = requests.get(url)

    data={'Results':False}
    # Parse the JSON response
    try:
        data = response.json()
    except:
        print(response.text)

    if data['Results']:
        # Define the starting URL for crawling
        start_url = data['Results'][0]["FirstURL"]
        print(start_url)
    else:
        # Construct the API endpoint URL and search query parameters
        params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_SEARCH_ENGINE_ID, "q": query}

        # Send the API request with authentication headers
        response = requests.get(endpoint, params=params)

        # Parse the JSON response and extract the search results
        json_data = response.json()
        try:
            search_results = json_data["items"]
        except Exception as e:
            print("daily quota runout")
        urls = []
        # Print the URLs of the search results
        for result in search_results:
            urls.append(result["link"])
        start_url = urls[0]
        print(start_url)
    
    return start_url

def url_validation(url):
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None # True or false


def extract_table(url):
    """
    Function to retrieve tables as a pandas dataframe from a given url
    """
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    dfs = pd.read_html(r.text)
    return dfs

def get_product_images(company_name):
    """
    Function to retrieve 5 image urls list from a given company name
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    num_results = 5
    search_type = "image"
    headers = {
        "Content-Type": "application/json"
    }

    # construct the query string
    query_string = f"{company_name} products or services"

    # make the request to the Google Custom Search API
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query_string,
        "num": num_results,
        "searchType": search_type
    }
    response = requests.get(search_url, params=params, headers=headers)

    # parse the response and get the image URLs
    image_urls = []
    if response.status_code == 200:
        results = response.json().get("items")
        if results:
            for result in results:
                image_urls.append(result.get("link"))

    return image_urls

if __name__ == '__main__':
    # Define a function to crawl a URL and extract relevant information
    query= 'Amazon'
    start_url = get_url_from_name(query)
    #image_urls = get_product_images(query)
    print(start_url)
