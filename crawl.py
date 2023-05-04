import pandas as pd
from urls_info_retrive import domain_extract
from urls_info_retrive import get_tag_text
from urls_info_retrive import get_url_from_name
import requests
from bs4 import BeautifulSoup


# Define a set to store visited URLs to avoid duplicates
visited_urls = set()
extracted_url = []
extract_domain = []
para_list = []
div_list = []
# Define a function to crawl a URL and extract relevant information
#query = "IKEA"
count = 0
#retrieving  images
# # Start crawling from the starting URL
def crawl(url):
    global df
    # Check if the URL has already been visited
    global count
    if url in visited_urls or count >= 10:
        return
    header = {
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
      "X-Requested-With": "XMLHttpRequest"}
    # Fetch the web page content
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract relevant information from the web page
        # For example, extracting all the links on the page
        links = soup.find_all("a")
        for link in links:
            link_url = link.get("href")
            if link_url:
              # Recursively crawl the extracted URL
              if link_url.startswith("https://"):
              # Process the extracted URL (e.g., store in a database, add to a queue)
                if link_url in extracted_url:
                  continue
                else:
                  # print(link_url)
                  para_dict = get_tag_text(url=link_url, page_source_text=soup, tag_text="p")
                  div_dict = get_tag_text(url=link_url, page_source_text=soup, tag_text="div")
                  extracted_url.append(link_url)
                  extract_domain.append(domain_extract(link_url))
                  para_list.append(para_dict)
                  div_list.append(div_dict)
                  # increment count recersion  
                  count = count + 1
                  # recersion
                  crawl(link_url)
    # Add the URL to the set of visited URLs
    output = {"url":extracted_url,"domain":extract_domain,
                             "tag_text_p":para_list, "tag_text_div":div_list}
    visited_urls.add(url)
    return visited_urls, output


if __name__ == "__main__":
  query = "IKEA"
  start_url = get_url_from_name(query)
  visited_url, output = crawl(url=start_url)
  print(visited_url)
  df = pd.DataFrame(data=output)
  print(df.head())
  print(df.shape)
  df.to_csv("extracted.csv")
