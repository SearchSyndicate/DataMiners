#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 21:17:09 2023

@author: apratim
"""

import os
from crunchbase_api import get_company_details
from urls_info_retrive import get_product_images
from flask_cors import CORS
from flask import Flask,request,render_template


ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
    """
    Renders a HTML page which allows us to input query.
    """
    return render_template('index.html')

@app.route('/predict' ,methods=['GET', 'POST'])
def predict():
    """
    Main API function which takes image from local storage with request and
    uses function pred for classification and covert the result to JSON format
    """
    text = request.form['text']

    search_type = request.form.get('scr_select')
    print(search_type)
    
    prediction = get_company_details(text)
    image_urls=[]
    if search_type=='With Images':
        image_urls = get_product_images(text)[:4]
    return render_template('result.html',prediction = prediction,image_urls=image_urls)

if __name__ == '__main__':
    app.run(debug=True)