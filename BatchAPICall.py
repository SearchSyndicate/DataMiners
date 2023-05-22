#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 20 16:47:47 2023

@author: Kapil
"""
import requests, json, time
import pandas as pd

def batch_call(df, n=50, sec_break=10, image=''):
    """
    Function to call crunchbase local api 'n' times in every 10 seconds 
    based on a dataframe (df) of inputs
    Params: 
        1. n: no. of inputs to be taken
        2. sec_break: time break between 2 API calls
    """
    df= df[:n]
    start_time = time.time()
    
    errors=[]
    desc_dict={}
    for index, row in df.iterrows():
        # Extract company name and country from the DataFrame
        company = df.loc[index,'Company']
        print(index+1, company)
        country = df.loc[index,'Country']
        url = df.loc[index,'URL']
        # Create the API request 
        response = requests.get(f"http://localhost:5000/predict?company={company}&country={country}&url={url}&image={image}")
        response.raise_for_status()
        print("status_code:", response.status_code)
        # Check if the response was successful
        if response.status_code==200:
            # Extract the descriptions the API response
            desc_dict[company] = json.loads(response.text)
        else:
            # Add the company to the error list
            errors.append((company,response.status_code))
        print(f"Taking a {sec_break} sec. break...{index+1}\n")
        time.sleep(sec_break)
        
        # Check if all inputs have been given
        if index == len(df) - 1:
            print("All inputs have been processed.")
            print(f"Execution time: --- {round((time.time() - start_time)/60,2)} minutes ---")
            return errors,desc_dict
        
if __name__ == '__main__':
    
    input_df = pd.read_csv("data/unicorn-company-list-with_URLs.csv",keep_default_na=False)
    #1st ensure that the Flask api is running 
    #image=y (if image urls are needed)
    errors,desc_dict = batch_call(input_df,sec_break=2)
    #final result
    desc_df = pd.DataFrame.from_dict(desc_dict,orient='index')