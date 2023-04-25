#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 19:12:50 2023

@author: Kapil
"""

import requests
import json


base_api_endpoint = "https://api.crunchbase.com/api/v4/"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-cb-user-key": "c72ba4be22ce7b9767ac7e5b88bdba07"
}

def get_uuid(query):
    """
    used for getting 1st returned uuid from API for a given company query
    """
    response = requests.get(base_api_endpoint+
                            f"autocompletes?query={query}&collection_ids=organizations",
                            headers=headers)
    data = json.loads(response.text)
    uuid = data['entities'][0]['identifier']['uuid']
    return uuid
    

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
                "values": [f"{get_uuid(api_query)}"],#UUID goes here
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
    api_query = "Amazon.com"
    data = get_company_details(api_query)