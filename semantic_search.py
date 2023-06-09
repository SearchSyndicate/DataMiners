## sementic search module
import re
from huggingchat import extract_info
from crawl import crawl_se_level
from crawl import crawl
import faiss
from transformers import AutoTokenizer, AutoModel
from datasets import Dataset
from langdetect import detect
from urls_info_retrive import get_url_from_name
from translation import aws_translation
from translation import non_api_translation
from huggingchat import key_words_extraction
from langdetect import detect
from serp_api import serp_response
##define module variable
# create a semnetic search function to retrieve most relative urls
try:
    model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
except:
    model_ckpt = "/home/muhamad/Search_Engine_competition/DataMiners/models"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt, model_max_length=512)
model = AutoModel.from_pretrained(model_ckpt)
    
# relative urls
def semantic_search_urls(extracted_url, query):
    # Convert the extracted url to a dataset
    dict_urls = {"urls": extracted_url}
    dataset_url = Dataset.from_dict(dict_urls)

    # Define a function for pooling the output of the model
    def cls_pooling(model_output):
        return model_output.last_hidden_state[:,0]

    # Define a function for getting embeddings
    def get_embeddings(url):
        encoded_input = tokenizer(url, padding=True, truncation=True, return_tensors="pt")
        encoded_input = {k: v for k,v in encoded_input.items()}
        model_output = model(**encoded_input)
        return cls_pooling(model_output)

    # Embed the dataset
    embeddings_dataset = dataset_url.map(
        lambda x: {"embeddings": get_embeddings(x["urls"]).cpu().detach().numpy()[0]})
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"{query} products, services and information (info)"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=10)
    return samples["urls"]



# here we define a semantic search over text which in df["tag_text_p"
# input will be the df get out of crawl function 
# Define a function for semantic search
def semantic_search_tags(list_text, query):
    if list_text:
        # Convert the extracted url to a dataset
        dict_urls = {"tags": list_text}
        dataset_url = Dataset.from_dict(dict_urls)

        # Define a function for pooling the output of the model
        def cls_pooling(model_output):
            return model_output.last_hidden_state[:,0]

        # Define a function for getting embeddings
        def get_embeddings(tag):
            encoded_input = tokenizer(tag, padding=True, truncation=True, return_tensors="pt")
            encoded_input = {k: v for k,v in encoded_input.items()}
            model_output = model(**encoded_input)
            return cls_pooling(model_output)

        # Embed the dataset
        embeddings_dataset = dataset_url.map(
            lambda x: {"embeddings": get_embeddings(x["tags"]).cpu().detach().numpy()[0]}
        )
        embeddings_dataset.add_faiss_index(column="embeddings")

        # Search for similar URLs
        question = f"what is {query} products and services?"
        question_embedding = get_embeddings([question]).cpu().detach().numpy()
        scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=2)

        # Return the search results
        return list(samples["tags"])
    else:
        return ""

def handle_text(text, chunk_size=2000):
    language = "en"
    text_to_enc = []
    for sub_text in text:
        sub_text = " ".join(sub_text)
        try:
            language = detect(sub_text)
        except Exception as e:
            pass
        if language != "en":
            try:
                sub_text = aws_translation(sub_text)
            except Exception as e:
                pass
        text_to_enc.extend([sub_text[i:i+chunk_size+100] for i in range(0, len(sub_text), chunk_size)])
    return text_to_enc

def clean_text(text):
    # remove newlines, tabs, and extra spaces
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\t+', ' ', text)
    text = re.sub(r' +', ' ', text)
    # remove URLs
    text = re.sub(r'http\S+', ' ', text)
    # remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # convert to lowercase
    #text = text.lower()
    return text

def get_semantic_urls(query, url = None):
    semantic_urls = []
    if not url:
        try:
            url = get_url_from_name(query)
        except:
            output, url_link, url = serp_response(query)              
    semantic_urls.extend([url])
    extracted_url = crawl(url=url)
    init_semantic_urls = semantic_search_urls(extracted_url=extracted_url, query=query)
    semantic_urls.extend(init_semantic_urls)
    return list(dict.fromkeys(semantic_urls))

def semantic_search(query, semantic_urls):
    output = crawl_se_level(semantic_urls)
    text_to_enc_p = handle_text(output["tag_text_p"])
    key_words = key_words_extraction(text_to_enc_p)
    sample_text_p = semantic_search_tags(list_text=text_to_enc_p, query=query)
    srt_text_p = " ".join(sample_text_p)
    semantic_text = clean_text(srt_text_p)
    return semantic_text, key_words
        
if __name__  == "__main__":
    query = "Horsch GmbH & Co. KG"
    semantic_urls = get_semantic_urls(query, "https://www.horsch.de/")
    print(semantic_urls)
    semantic_txt, key_words = semantic_search(query,semantic_urls)
    #output = extract_info(semantic_txt = semantic_txt, query=query)
    print(semantic_txt)
   
   
   #tokenizer.save_vocabulary("/home/muhamad/Search_Engine_competition/DataMiners/models")
   #model.save_pretrained("/home/muhamad/Search_Engine_competition/DataMiners/models")
   # to load tokenizer "tokenizer = AutoTokenizer.from_pretrained("./models/tokenizer/")"
   # load the model "model = AutoModel.from_from_pretrained("./models/checkpoint/")
