import requests
import json


def serp_response(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": query})
    headers = {
    'X-API-KEY': '9dc856d842208a0d2b252e6af8b84aa8dd56d740',
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
    
    # retrive a wikibedia_link
    try:
        wiki_link = response_json["knowledgeGraph"]["descriptionLink"]
        wiki_link = wiki_link.split(",")[0]
    except: wiki_link = ""
    
    # that give us a products most of time
    try:
        for i in range(len(response_json["organic"][0]["sitelinks"])):
            title_sitelink = response_json["organic"][0]["sitelinks"][i]["title"]
    except: title_sitelink = ""
    return com_type, descrabtion, snip, title_sitelink, wiki_link

if __name__ == "__main__":
    com_type, descrabtion, snip, title_sitelink, wiki_link = serp_response("twitter")
    print(com_type)
    print(descrabtion)
    print(snip)
    print(title_sitelink)
    print(wiki_link) 
    # com_text = get_wiki_text(output[-1])
    # print("###################################")
    # print(com_text)