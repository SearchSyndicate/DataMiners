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

base_api_endpoint = "https://api.crunchbase.com/api/v4/"

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

def get_uuid(query):
    """
    used for getting 1st returned uuid from API for a given company query
    """
    response = requests.get(base_api_endpoint+
                            f"autocompletes?query={query}&collection_ids=organizations&limit=25",
                            headers=headers)
    data = json.loads(response.text)
    if data['count']== 1:
        uuid = data['entities'][0]['identifier']['uuid']
        similar_companies = (data['entities'][0]['identifier']['value'],
                              data['entities'][0]['short_description'])
    elif data['count']> 1:
        # removing dissimilar companies based on length and characters similarity
        similar_companies = [(i['identifier']['value'],i['short_description']) 
                              for i in data['entities'] 
                              if name_comparison_score(i['identifier']['value'],query)>0.15]
    else:
        uuid='No results for given query'
        
    return similar_companies, uuid
    

def get_company_details(api_query): 
    """
    returns company details based on an input query using get_uuid()
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
                           "Description":company_description}
    else:
        company_details = "No results for this query"
    
    return company_details



if __name__ == '__main__':
    api_query = "Amazon.com, Inc., USA"
    similar_companies, uuid = get_uuid(api_query)
    data = get_company_details(api_query)
