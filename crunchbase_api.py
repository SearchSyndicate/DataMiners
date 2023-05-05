#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 19:12:50 2023

@author: Kapil

Works best only for a single company name. It gets confused with some other company 
if more informations are given like country etc.
"""

import requests
import json
import re
import pandas as pd
import time
from youdotcom import Chat

base_api_endpoint = "https://api.crunchbase.com/api/v4/"
you_api_key="H63327XXYJEH2FB3B3ISHR8FITIMJR2VREA"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-cb-user-key": "c72ba4be22ce7b9767ac7e5b88bdba07"
}

def removeSpecialChars(string):
    clean_string = re.sub(r"[^a-zA-Z0-9]+", ' ', string).lower().strip()
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

def get_uuid(query, comp=True):
    """
    used for getting 1st returned uuid from API for a given company query
    and all descriptions of resembling companies upto 25
    Parameter: comp is there to decide whether to use name_comparison_score or not
    """
    response = requests.get(base_api_endpoint+
                            f"autocompletes?query={query}&collection_ids=organizations&limit=25",
                            headers=headers)
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
                [(i['identifier']['value'],i['short_description']) 
                                     for i in data['entities']]
    return similar_companies, uuid

def get_products_from_text(text):
    """
    Function to extract Product/Services from a text
    """
    prompt = f"""
    Your task is to help a marketing team extract useful informations
    from a given text.
    You have to perform the following actions: 
    1. Identify the following items from the text: 
        - list of Products sold by the company separated by commas.
        - list of Services offered by the company separated by commas.
        - list of Keywords about the Products or Services of the company 
          separated by commas.
    
    2. Make each item of the above lists one or two words long, if possible. 

    3. Format your response only as a JSON object with \
        "Products", "Services" and "Keywords" as the keys. 
        If the information isn't present, use "unknown" \
        as the value.
        Make your response as short as possible without any explanation.
        
    text: '''{text}'''
    """
    
    chat = Chat.send_message(message=prompt, api_key=you_api_key)
    if chat['status_code']==200:
        output = chat['message']
    else:
        error = f"{chat['status_code']} error occurred"
        output = {'Products':error, 'Services':error}
    return output

def get_company_details(api_query): 
    """
    returns company details based on an input query using get_uuid()
    gives location in addition description
    """
    payload = {
        "field_ids": ["identifier", "location_identifiers", "short_description",
                      "linkedin"],
        "query": [
            {
                "type": "predicate",
                "values": [f"{get_uuid(api_query)[1]}"],#UUID goes here
                "field_id": "uuid",
                "operator_id": "includes"
            },
            {
                "type": "predicate",
                "values": ["company"],
                "field_id": "facet_ids",
                "operator_id": "includes"
            }
        ],
        "order": [
            {
                "sort": "asc",
                "nulls": "last",
                "field_id": "rank_org"
            }
        ],
        "limit": 1000
    }
    response = requests.post(url = base_api_endpoint+"searches/organizations", 
                             json=payload, headers=headers)
    
    data = json.loads(response.text)
    
    if len(data['entities'])>0:
        company_name = data['entities'][0]['properties']['identifier']['value']
        company_location = ", ".join([i['value'] for i in data['entities'][0]['properties']['location_identifiers']])
        company_description = data['entities'][0]['properties']['short_description']
        company_details = {"Name":company_name,
                           "Location":company_location,
                           "Products/Services":get_products_from_text(company_description)}
    else:
        company_details = {"Error":"No results for this query"}
    
    return company_details

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
    if uuid !='No results for given query':
        data = get_company_details(api_query)
        print(data)
        
