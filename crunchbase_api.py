#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 19:12:50 2023

@author: Kapil
"""

import requests
import json
import re
import pandas as pd
import time
from urls_info_retrive import domain_extract
from hugchat import hugchat
from semantic_search import semantic_search
from GPTturboAPI import openai_api


base_api_endpoint = "https://api.crunchbase.com/api/v4/"
you_api_key="BPG53UN1C6PVAQ0R6A11PH4E9JF396YNXAI"

def get_headers():
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-cb-user-key": "c72ba4be22ce7b9767ac7e5b88bdba07"
    }
    return headers

def removeSpecialChars(string):
    clean_string = re.sub(r"[^a-zA-Z0-9]+", ' ', str(string)).lower().strip()
    return clean_string

def name_comparison_score(name1,name2):

    name1_clean = removeSpecialChars(name1)
    name2_clean = removeSpecialChars(name2)
    name1_tokens = name1_clean.split(' ')
    name2_tokens = name2_clean.split(' ')
    length_1 = len(name1_tokens)
    length_2 = len(name2_tokens)
    score=0
    for i in name1_tokens:
        if i.lower() in [x.lower() for x in name2_tokens] and i not in '':
            score+=1
    return score/(length_1+length_2)

def get_main_company_name(company_name):
    """
      function to remove any abbreviations of legal entities types
    """
    with open('data/Entity_Legal_Names.txt') as f:
        entity_abbreviations = eval(f.readlines()[0])
    
    # Remove any entity type abbreviations from the company name
    company_words = company_name.split()
    main_words = []
    for word in company_words:
        word=word.replace(",","")
        #remove .com etc. from the names
        if "." in word:
            word = domain_extract(word)
        if word.lower() not in entity_abbreviations:
            main_words.append(word)
    main_company_name = " ".join(main_words)
    
    return main_company_name

def get_uuid(query, comp=True):
    """
    used for getting 1st returned uuid from API for a given company query
    and all descriptions of resembling companies upto 25
    Parameter: comp is there to decide whether to use name_comparison_score or not
    """
    response = requests.get(base_api_endpoint+
                            f"autocompletes?query={query}&collection_ids=organizations&limit=25",
                            headers=get_headers())
    similar_companies=None
    uuid='No results for given query'
    if response.status_code == 200:
        data = json.loads(response.text)
        uuid = data['entities'][0]['identifier']['uuid']
        if data['count']== 1:
            similar_companies = [(data['entities'][0]['identifier']['value'],
                                  data['entities'][0]['short_description'])]
        elif data['count']> 1:
            # removing dissimilar companies based on length and characters similarity
            if comp:
                similar_companies = [(i['identifier']['value'],i['short_description']) 
                                      for i in data['entities'] 
                                   if name_comparison_score(i['identifier']['value'],query)>0.15]
            else:
                similar_companies = [(i['identifier']['value'],i['short_description']) 
                                     for i in data['entities']]
    return similar_companies, uuid

def is_json(myjson):
  """
    function to check if a string is JSON
  """
  myjson = str(myjson).replace("'",'"')
  try:
    json.loads(myjson)
  except ValueError as e:
      print(str(e))
      return False
  return True



def prompting(prompt,company,semantic_urls, helper=False):
    """
    Prompts OpenAI 1st then in case of failure prompts Youchat
    and in case of failure in both, finally calls huggingchat 
    """
    
    output=None
    if helper:
        try:
            api="OpenAI"
            output = openai_api(prompt)
            print(type(output))
            print(api, output)
        except:
            output, key_words = semantic_search(company, semantic_urls)
            print("semantic_search", output)
     
    if output==None :
        print(f"output={None} exception occurred in OpenAI " )
        
        api="Youchat"
        chat = "{api} API down"
        response =requests.get(f"https://api.betterapi.net/youchat?inputs={prompt}&key={you_api_key}",
                           headers=get_headers())
        chat= json.loads(response.text)
        if chat['status_code']==200 and 'str' not in str(type(chat))\
        and 'sorry' not in str(chat): 
            output = chat['generated_text']
            print(type(chat))
            print(api, output)
            output = json.loads(re.search('({.+})', ' '.join(output.split('\n')).strip()).group(0).replace("'", '"'))
            if not helper and not is_json(output):
                error = f"{chat} error occurred"
                output = {'Products':error, 'Services':error, 'Keywords':[]}
        else:
            output="{'Keywords':[]}"
        output =  {k.lower(): v for k, v in output.items()}
        keywords_len=0    
        if is_json(output):
            keywords_len = len(eval(str((output)))['keywords'].split())
        #check to prevent LLM Hallucinations
        if not len(output)>0 or keywords_len<4 or \
        not all(k in output for k in ("products","services","keywords")):
            try:
                api="hugchat"
                chatbot = hugchat.ChatBot(cookie_path="API_cookies/cookies.json")
                # Create a new conversation
                id = chatbot.new_conversation()
                chatbot.change_conversation(id)
                output = (chatbot.chat(json.dumps({"chat":prompt})))
                print(type(output))
                print(api, output)
            except:
                error = "Hugchat down"
                output = {'Products':error, 'Services':error}
        
    return output

def get_products_from_text(text, company, country, semantic_urls):
    """
    Function to extract Product/Services from a text
    """
    
    helper_prompt = f"""You have to perform the following actions: 
        1. Give a list of the products and services offered by {company}. 
        2. limit your words to only relevant words. """
    sample = prompting(helper_prompt, company, semantic_urls, helper=True)
    
    if text!=None:
        prompt = f"""
        Your task is to help a marketing team to give useful informations
        about {company}.
        You have to perform the following actions: 
            
        1. Share the following informations about {company}:  
            - list of Products sold by {company} across {country if country !="" else "the world"} separated by commas.
            - list of Services offered by {company} across {country if country !="" else "the world"} separated by commas.
            - list of Keywords about the Products or Services of the {company} separated by commas.
              
        2. You must identify atleast one item either from Products or Services.
            There's no upper limit as long as they are relevant.
        
        3. Make your response as accurate as possible without any explanation or notes.
    
        4. Format your response only as one JSON object with 
            only "Products", "Services" and "Keywords" as the keys. 
            If the information isn't present in the test, use "unknown" as the value.
            
        text: '''{text}'''
        other helpful text: '''{sample}'''
        """
    else:
        prompt = f"""
        Your task is to help a marketing team to give useful informations
        about {company}.
        You have to perform the following actions: 
            
        1. Share the following informations about {company}: 
            - Extract a brief description about {company} in a sentence from the given text.
            - list of Products sold by {company} across {country if country !="" else "the world"} separated by commas.
            - list of Services offered by {company} across {country if country !="" else "the world"} separated by commas.
            - list of Keywords about the Products or Services of the {company} separated by commas.
              
        2. You must identify atleast one item either from Products or Services.
            There's no upper limit as long as they are relevant.
        
        3. Make your response as accurate as possible without any explanation or notes.
    
        4. Format your response only as one JSON object with 
            only "Description", "Products", "Services" and "Keywords" as the keys. 
            If the information isn't present in the test, use "unknown" as the value.
            
        text: '''{sample}'''
        """
    time.sleep(5)
    output = prompting(prompt, company, semantic_urls)
    return output



def batch_call_api(df):
    """
    Function to call crunchbase api 25 times in every minute 
    max limit is 25
    """
    errors=[]
    desc_df=pd.DataFrame(columns=['company', 'description'])
    for index, row in df.iterrows():
        # Extract the query with company name and country from the DataFrame
        query = input_df.loc[index,'queries']
        if index % 25 == 0:
            # Create the API request 
            similar_companies, uuid = get_uuid(query, comp=False)
    
            # Check if the response was successful
            if similar_companies:
                # Extract the descriptions the API response
                desc_df = pd.concat([desc_df,
                          pd.DataFrame(similar_companies, columns=['company', 'description'])],
                          ignore_index=True)
                if uuid!='No results for given query':
                    df.loc[index,'uuid'] = uuid
                else:
                    df.loc[index,'uuid'] = ''
            else:
                # Add the company to the error list
                errors.append(query)
            print(f"Taking a minute break...{index/25}")
            time.sleep(60)
    
        # Check if all inputs have been given
        if index == len(df) - 1:
            print("All inputs have been processed.")
            return errors, df,desc_df


if __name__ == '__main__':
    batch_calling=False
    
    if batch_calling: 
        input_df = pd.read_csv("data/unicorn-company-list.csv",keep_default_na=False)
        input_df['queries']=input_df.apply(lambda x: x['Company']+", "+x['Country'],axis=1)
        errors, df,desc_df = batch_call_api(input_df)
    
    api_query = "Amazon.com, Inc., USA"
    similar_companies, uuid = get_uuid(api_query)
    print(similar_companies)
