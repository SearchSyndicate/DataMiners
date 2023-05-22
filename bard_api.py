import os
from bardapi import Bard
import requests

#bard_token = "Wgh_oONK6LFFZpxjYymYYdJuEEAMGyIxTROlac1hEJBaiFTNO6qEDQzTTeDaLOLD1maoOQ."

def bard_api(prompt):
    prompt_l = prompt.split()
    if len (prompt_l) > 4049:
        prompt = " ".join(prompt_l[0:4049])
    os.environ['_BARD_API_KEY'] = bard_token
    # token='xxxxxxxxxxx'
    session = requests.Session()
    session.headers = {
                "Host": "bard.google.com",
                "X-Same-Domain": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Origin": "https://bard.google.com",
                "Referer": "https://bard.google.com/",
            }
    session.cookies.set("__Secure-1PSID", os.getenv("_BARD_API_KEY")) 
    # session.cookies.set("__Secure-1PSID", token) 
        
    bard = Bard(session=session, timeout=30)
    ans = bard.get_answer(prompt)['content']
    try:
        ans = ans.split("```json")[1]
        ans = ans.split("```")[0]
    except:
        try:
            ans = ans.split("json")[1]
        except:
            print(ans)
    return ans


if __name__ == "__main__":
    semantic_txt = '''Yandex is a technology company based in Russia that provides a wide range of online services and products. It was founded in 1997 by Arkady Volozh and Ilya Segalovich and has since grown to become one of the largest and most influential technology companies in Russia and neighboring countries.
Here are some key aspects of Yandex:
Search Engine: Yandex operates the largest search engine in Russia, accounting for the majority of web searches in the country. Similar to Google, Yandex offers search results, ads, maps, and other related services.
Online Services: Yandex offers a variety of online services, including email (Yandex.Mail), cloud storage (Yandex.Disk), news (Yandex.News), translation (Yandex.Translate), video hosting (Yandex.Video), and more. These services cater to the needs of individual users as well as businesses.
Ride-Hailing and Food Delivery: Yandex operates Yandex.Taxi, a popular ride-hailing service in Russia and other countries. Additionally, Yandex.Food provides online food delivery services in partnership with local restaurants.
Advertising: Yandex has a significant presence in the digital advertising market. It offers advertising solutions through its advertising platform, including contextual ads, display ads, video ads, and more.
Technology and AI: Yandex heavily invests in research and development, particularly in the field of artificial intelligence (AI). They have developed their own AI technologies, including machine learning algorithms, computer vision, speech recognition, and natural language processing.
Maps and Navigation: Yandex.Maps provides mapping and navigation services, similar to Google Maps. It offers detailed maps, traffic information, and route planning features.
E-commerce: Yandex operates Yandex.Market, an online marketplace where users can compare prices and make purchases from various online retailers.
Yandex has established itself as a prominent player in the Russian technology industry, offering a wide range of services to millions of users. With its focus on search, online services, ride-hailing, and AI, Yandex continues to innovate and expand its presence both within Russia and internationally.'''
    
    query = 'Yandex'
    
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
    5. Format your response only as a JSON object with \
        "description","Products", "Services" and "Keywords" as the keys. 
        If the information isn't present in the test, use "unknown" \
        as the value.      
    text: '''{semantic_txt}'''
    """
    
    from bardapi import Bard
    token = 'Wgh_oONK6LFFZpxjYymYYdJuEEAMGyIxTROlac1hEJBaiFTNO6qEDQzTTeDaLOLD1maoOQ.'
    bard = Bard(token=token)
    result = bard.get_answer(prompt)['content']
    print(result)
    
    # for _ in range(10):
    #     try:
    #         response = bard_api(prompt=prompt)
    #         print(response)
    #     except Exception as e:
    #         print(e)
