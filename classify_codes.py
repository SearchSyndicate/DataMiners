#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 00:26:30 2023

@author: kapil
"""

import pandas as pd
import json, re
from gpt4free import italygpt
from hugchat import hugchat
italygpt = italygpt.Completion()

# Load the SIC and NAICS keyword lists
sic_dict = json.load( open( "data/SIC_codes.json" ) )
sic_df = pd.DataFrame(sic_dict.items(),columns=['SIC_codes','Company_type'])
naics_df = pd.read_csv('data/6 Digit NAICS-2017.csv')

# Define a function to match the preprocessed text data with the keyword lists
def match_keywords(text, keywords):
    matches = [kw for kw in keywords if kw.lower() in text]
    return matches

# Define a function to classify the company into SIC and NAICS codes
def classify_company(company_data,company):
    """
      function to extract industry codes from text using
      1. LLMs (italygpt and hugchat as backup)
      2. string matching
    """
    prompt = f"""You have to perform the following actions: 
                 1. Give a list of the Standard Industrial Classification (SIC) 
                 and North American Industry Classification System (NAICS) 2017 codes 
                 that are applicable to {company} as a company.
                 2. You can get relevant information about the company from text here: '''{company_data}'''
                 3. Keep your response limited to only the numerical codes."""
    # initialize api
    italygpt.init()
    
    # get an answer
    italygpt.create(prompt=prompt)   
    answer=italygpt.answer
    print("italygpt",answer)                     
    code_text = re.findall(r'\d+', answer) 
    if len(code_text)==0 or 'sorry' in answer:
        chatbot = hugchat.ChatBot()
        # Create a new conversation
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        answer = chatbot.chat(prompt)
        print("hugchat",answer)       
        code_text = re.findall(r'\d+', answer) 
    sic_code = [i for i in code_text if len(i)==4]
    naics_code = [i for i in code_text if len(i)!=4]
    
    if len(sic_code)==0 and len(naics_code)==0:
        
        sic_matches = match_keywords(company_data, sic_df['Company_type'])
        naics_matches = match_keywords(company_data, naics_df['Title'])
    
        sic_code = sic_df.loc[sic_df['Company_type'].isin(sic_matches), 
                              'SIC_codes'].iloc[0] if len(sic_matches) > 0 else []
        naics_code = naics_df.loc[naics_df['Title'].isin(naics_matches), 
                                  'NAICS_Codes'].iloc[0] if len(naics_matches) > 0 else []
    sic_code = list(set(sic_code))
    naics_code = list(set(naics_code))
    return sic_code, naics_code







