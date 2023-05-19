#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 21:17:09 2023

@author: Kapil
"""

import os, requests, json
from crunchbase_api import (get_uuid, get_headers, get_main_company_name, get_products_from_text,
                            removeSpecialChars, is_json, name_comparison_score)
from urls_info_retrive import get_product_images,domain_extract, url_validation
from flask_cors import CORS
from threading import Thread
from classify_codes import classify_company
from flask import Flask,request,render_template
from semantic_search import get_semantic_urls

base_api_endpoint = "https://api.crunchbase.com/api/v4/"
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder='static')
app.config['JSON_SORT_KEYS'] = False
status = None

CORS(app)

def get_company_details(api_query, country, url_text): 
    """
    returns company details based on an input query using get_uuid() from crunchbase api 
    gives location in addition description
    """
    global status
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
                             json=payload, headers=get_headers())
    data = json.loads(response.text)
    
    url_dict={}
    if len(data['entities'])>0 and\
        name_comparison_score(data['entities'][0]['properties']['identifier']['value'],api_query)>0.25:
        status = 1
        company_name = get_main_company_name(data['entities'][0]['properties']['identifier']['value'])
        status = 2
        company_location = ", ".join([i['value'] for i in data['entities'][0]['properties']['location_identifiers']])
        company_description = data['entities'][0]['properties']['short_description']
        related_urls = get_semantic_urls(company_name)
        status = 4
        company_products = get_products_from_text(company_description, company_name, country, related_urls)
        status = 6
        company_codes = classify_company(removeSpecialChars(company_products),company_name)
        print(company_codes,"company_codes")
        status = 7
        company_details = {"Name":company_name,
                           "HQ Location":company_location,
                           "Description" : company_description,
                           "SIC Codes":company_codes[0],
                           "NAICS Codes":company_codes[1]}
    else:
        status = 5
        if len(url_text)>0 and url_validation(url_text):
            related_urls = get_semantic_urls(api_query, url_text)
        else:
            related_urls = get_semantic_urls(api_query)
            
        status = 6
        company_products = get_products_from_text(None, api_query, country, related_urls)
        status = 7
        company_codes = classify_company(removeSpecialChars(company_products),api_query)
        print(company_codes,"company_codes")
        company_details = {"Name":api_query,
                           "SIC Codes":company_codes[0],
                           "NAICS Codes":company_codes[1]}
    status = 8
    if is_json(str(company_products)):
        company_products = json.loads(str(company_products).replace("'", '"'))
        company_details.update(company_products)
    else:
        company_details.update({"Products/Services":company_products})
        
    url_dict = {"Related URLs":list(set(related_urls))[:4]}
    status = 9
   
    return company_details, url_dict

@app.route('/')
def home():
    t1 = Thread(target=get_company_details)
    t1.start()
    """
    Renders a HTML page which allows us to input query.
    """
    return render_template('index.html')

@app.route('/predict' ,methods=['GET', 'POST'])
def predict():
    """
    Main API function which takes input from UI or endpoint with request and
    uses function 'get_company_details' to get the result in JSON format
    """
    print(""""give params for company as per this sample:
    predict?company=Amazon&country=USA&url=https://www.amazon.com/""")
    ui = False
    #inputs
    try:
        company_text = request.form['company_text']
        ui = True
    except:
        company_text = request.args.get('company')
        
    try:
        country_text = request.form['country_text']
        ui = True
    except:
        country_text = request.args.get('country')
    
    try:
        url_text = request.form['url_text']
        ui = True
    except:
        url_text = request.args.get('url')
        
    text = company_text
    
    #check if the input is an url 
    #if so then domain name will be the input query
    if url_text!='' and domain_extract(url_text):
        text = domain_extract(url_text)
    #if only country text is given 
    #then country name will be the input query
    elif company_text+url_text+country_text==country_text:
        text = country_text
        
    search_type = request.form.get('scr_select')
 
    prediction, url_dict = get_company_details(text, country_text, url_text)
    print(url_dict,"url_dict")    
    image_urls=[]
    if search_type=='With Images' or ui == False:
        image_urls = get_product_images(prediction["Name"])[:4]
    if ui:
        final_result= render_template('result.html',prediction = prediction,image_urls=image_urls, url_dict=url_dict)
    else:
        prediction.update(url_dict)
        if len(image_urls)>0:
            prediction.update({"image_urls":image_urls})
        final_result = json.dumps(prediction)
    return final_result

@app.route('/status', methods=['GET'])
def getStatus():
  statusList = {'status':status}
  return json.dumps(statusList)


if __name__ == '__main__':
    #example
    #http://127.0.0.1:5000/predict?company=Amazon&country=USA&url=https://www.amazon.com/
    app.run(debug=True,host='0.0.0.0')