from hugchat import hugchat
from summa import keywords
import json
        
def key_words_extraction(text):
    text = " ".join(text)
    TR_keywords = keywords.keywords(text, scores=True)
    key_words = [x for x, y in TR_keywords]
    return key_words

def extract_info(semantic_txt, query):
    semantic_txt_l = semantic_txt.split()
    if len (semantic_txt_l) > 901:
        semantic_txt = " ".join(semantic_txt_l[0:900])
    prompt = {'message':[{'role':'assistant', 'content': f"""
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
    """}]}
    chatbot = hugchat.ChatBot(cookie_path="API_cookies/cookies.json")
    # Create a new conversation
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    output = (chatbot.chat(json.dumps({"chat":prompt})))
    return output  

if __name__ == '__main__':
    text = '''Cleaning tools Bosch brings together comprehensive expertise in vehicle technology
            with hardware software and services to offer complete mobility solutions Bosch offers innovative products and services for
            industry and trades Bosch offers innovative products and services for industry and trades We look forward to your inquiry 
            Explore Boschs wide range of products and solutions for your market and industry Heating cooling and wellbeing Power tools
            Measuring tools Bosch brings together comprehensive expertise in vehicle technology with hardware software and services to 
            offer complete mobility solutions Explore Boschs wide range of products and solutions for your market and industry Garden tools 
            Home appliances Smart Home Find our PGP Key hereFingerprint F40C 0FE3 E919 B082 B2DD 75E5 929D 3AFD 217E 21D7 The Bosch Product Security Incident 
            Response Team PSIRT is the central point of contact for external security researchers partners and customers to report cybersecurity
            information related to products developed by Bosch and its brands Responsible disclosure of vulnerabilities has longerterm
            benefits because it allows us to fix vulnerabilities inform customers about fixes and continuously improve security in 
            our products If you believe you have identified a potential vulnerability or security issue in a Bosch product or 
            service please contact us using our Vulnerability Reporting process We strongly encourage you to encrypt all communication
            with the Bosch PSIRT Our SMIME and PGP public keys and fingerprints are available at the bottom of each page Search our
            SMIME key hereFingerprint 87F16F7060D294838IKEA Family is for everyone. From those whose homes are their passion, to those who are just starting out and need a helping hand. Just by being a member you’ll receive discounts on many products! 

2AC69F546867C807F861DF0'''
    output = extract_info(semantic_txt=text, query="Bosch Germany")
    print(type(output))
    print(output)
    # chatbot = hugchat.ChatBot(cookie_path="API_cookies/cookies.json")  # or cookies=[...]
    # #print(chatbot.chat(json.dumps({"chat":"Who is Michael Jordan?"})))
    # print(chatbot.chat("what is linux"))

    # # Create a new conversation
    # id = chatbot.new_conversation()
    # chatbot.change_conversation(id)
