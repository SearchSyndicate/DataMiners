import requests
import bardapi
import os

api_key = "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"

def openai_api(semantic_txt, query):
    semantic_txt_l = semantic_txt.split()
    if len (semantic_txt_l) > 901:
        semantic_txt = " ".join(semantic_txt_l[0:900])
    prompt = f"""
    Your task is to help a marketing team extract useful informations
    from a given text.
    You have to perform the following actions: 
    1. Identify the following items from the text:
        - extract a brief description about {query}
        - list of Products sold by {query} separated by commas.
        - list of Services offered by {query} separated by commas.
        - list of Keywords about the Products or Services of {query} 
          separated by commas.
          
    2. You must identify atleast one item in text either from Products or Services.
    
    3. Make each item of the above lists one or two words long, if possible. 
    
    4. Make your response as short as possible without any explanation or notes.



def openai_api(prompt):
    api_key = "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"
    prompt = prompt.split()
    if len (prompt) > 4090:
        prompt = " ".join(prompt[0:4090])
    
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
        }
    data = {'model': 'gpt-3.5-turbo',
        "messages":[
            {"role": "assistant", "content": f"{prompt}"}]}
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        json=data)

    result = response.json()
    return result['choices'][0]['message']['content']

if __name__ == '__main__':
    semantic_txt = ''
    query=''
    prompt = """
