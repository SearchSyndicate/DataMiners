#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 00:26:30 2023

@author: kapil
"""

import pandas as pd
import json

# Load the SIC and NAICS keyword lists
sic_dict = json.load( open( "data/SIC_codes.json" ) )
sic_df = pd.DataFrame(sic_dict.items(),columns=['SIC_codes','Company_type'])
naics_df = pd.read_csv('data/6 Digit NAICS-2017.csv')

# Define a function to match the preprocessed text data with the keyword lists
def match_keywords(text, keywords):
    matches = [kw for kw in keywords if kw.lower() in text]
    return matches

# Define a function to classify the company into SIC and NAICS codes
def classify_company(company_data):

    sic_matches = match_keywords(company_data, sic_df['Company_type'])
    naics_matches = match_keywords(company_data, naics_df['Title'])

    sic_code = sic_df.loc[sic_df['Company_type'].isin(sic_matches), 'sic_code'].iloc[0] if len(sic_matches) > 0 else None
    naics_code = naics_df.loc[naics_df['Title'].isin(naics_matches), 'naics_code'].iloc[0] if len(naics_matches) > 0 else None

    return sic_code, naics_code
