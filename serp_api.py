import requests
import json
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from translation import aws_translation
from translation import non_api_translation
from langdetect import detect

# Load environment variables from .env file
load_dotenv()
serp_api_key = os.environ.get('SERP_API_KEY')

def serp_response(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": query})
    headers = {
    'X-API-KEY': serp_api_key,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = json.loads(response.text)
    
    # extract website_link
    try:
        website_link = response_json["knowledgeGraph"]["website"]
    except: website_link = None
    # type of tech company
    try:
        com_type = response_json["knowledgeGraph"]["type"]
    except: com_type = ""
    
    # describation about the company
    try:
        descrabtion = response_json["knowledgeGraph"]["description"]
    except: descrabtion = ""
    
    # a large text to pass for llm
    try:
        snip = ""
        for i in range(len(response_json["organic"])):
            snip += response_json["organic"][i]["snippet"]
            snip += " "
    except: snip = ""
    try:
        wiki_link = response_json["knowledgeGraph"]["descriptionLink"]
        wiki_link = wiki_link.split(",")[0]
    except: wiki_link = ""
    
    # scrap wikipedia text
    try:
        text  = wiki_scrap(wiki_link)
    except:
        text = ""
    
    #image link
    try:
        url_link = response_json["knowledgeGraph"]["imageUrl"]
    except: url_link = ""
    
    output = " ".join([com_type, descrabtion, snip, text])
    #translating output text
    output_text=[]    
    for text in output.split("..."):
        try:
            language = detect(text)
        except Exception as e:
            print(e)
            language = "en"
        if language != "en":
            try:
                text = aws_translation(text)
            except Exception as e:
                print(e)
                text = non_api_translation(text)
        output_text.append(text)
    output = " ".join(output_text)
    return output, url_link, website_link

def wiki_scrap(url):
    text = ""
    try: 
        url_open = requests.get(url)
    except: 
        return text   
    if url_open.status_code == 200:
        soup = BeautifulSoup(url_open.content, 'html.parser')
        details = soup('table', {'class': 'infobox'})
        for i  in details:
            h = i.find_all('tr')
            for j in h:
                heading = j.find_all('th')
                details = j.find_all('td')
                if heading is not None and details is not None:
                    for x, y in zip(heading, details):
                        text += x.text + ":" + y.text +"," + " " 
            for i in range(1,2):
                text += " " + soup('p')[i].text
    return text

if __name__ == "__main__":
    # text = serp_response("twitter")
    # print(text)
    text, url_link = serp_response("Horsch GmbH & Co. KG")
    print(text)
    # com_text = get_wiki_text(output[-1])
    # print("###################################")
    # print(com_text)
