from hugchat import hugchat

def extract_info(semantic_txt, query):
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

    5. Format your response only as a JSON object with \
        "description","Products", "Services" and "Keywords" as the keys. 
        If the information isn't present in the test, use "unknown" \
        as the value.
        
    text: '''{semantic_txt}'''
    """
    chatbot = hugchat.ChatBot()
    # Create a new conversation
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    output = (chatbot.chat(prompt))
    return output  