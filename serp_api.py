import requests
import json
import os
from dotenv import load_dotenv
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
    
    return " ".join([com_type, descrabtion, snip])

if __name__ == "__main__":
    text = serp_response("twitter")
    print(text)

    # com_text = get_wiki_text(output[-1])
    # print("###################################")
    # print(com_text)