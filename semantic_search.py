## sementic search module
import re
from crawl import crawl_se_level
from crawl import crawl
import faiss
from transformers import AutoTokenizer, AutoModel
from datasets import Dataset
from langdetect import detect
from urls_info_retrive import get_url_from_name
from translation import aws_translation
from translation import non_api_translation
##define module variable
# create a semnetic search function to retrieve most relative urls
#model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
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
    question = f"{query} products and service"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=10)
    return samples["urls"]



# here we define a semantic search over text which in df["tag_text_p"
# input will be the df get out of crawl function 
# Define a function for semantic search
def semantic_search_tags(list_text, query):
    # Convert the extracted url to a dataset
    dict_urls = {"tags": list_text}
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
        lambda x: {"embeddings": get_embeddings(x["tags"]).cpu().detach().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"what is {query} products and services?"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=2)

    # Return the search results
    return list(samples["tags"])
# here we define a semantic search over text which in df["tag_text_div"
# input will be the df get out of crawl function 
# Define a function for semantic search
# Define a function for semantic search div data
def semantic_search_div(list_text, query):
    # Convert the extracted url to a dataset
    dict_urls = {"div": list_text}
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
        lambda x: {"embeddings": get_embeddings(x["div"]).cpu().detach().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = "What are the products and services of the company?"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=2)

    # Return the search results
    return list(samples["div"])


def handle_text(text, chunk_size=2000):
   text_to_enc = []
   for sub_text in text:
      sub_text = " ".join(sub_text)
      #sub_text = non_api_translation(sub_text)
      text_to_enc.extend([sub_text[i:i+chunk_size+100] for i in range(0, len(sub_text), chunk_size)])
   return text_to_enc


def semantic_search(query):
    start_url = get_url_from_name(query)
    extracted_url = crawl(url=start_url)
    samples_urls = semantic_search_urls(extracted_url=extracted_url, query=query)
    output = crawl_se_level(samples_urls)
    text_to_enc_p = handle_text(output["tag_text_p"])
    text_to_enc_div = handle_text(output["tag_text_div"])
    sample_text_p = semantic_search_tags(list_text=text_to_enc_p, query=query)
    sample_text_div = semantic_search_div(list_text=text_to_enc_div, query=query)
    srt_text_p = " ".join(sample_text_p)
    srt_text_div = " ".join(sample_text_div)
    srt_text = srt_text_p + " " + srt_text_div
    srt_text = clean_text(srt_text)
    return srt_text     
        
if __name__  == "__main__":
    query = "amazon"
    sample = semantic_search(query)
    print(sample)
   #print(sample_text)
   #tokenizer.save_vocabulary("/home/muhamad/Search_Engine_competition/DataMiners/models")
   #model.save_pretrained("/home/muhamad/Search_Engine_competition/DataMiners/models")
   # to load tokenizer "tokenizer = AutoTokenizer.from_pretrained("./models/tokenizer/")"
   # load the model "model = AutoModel.from_from_pretrained("./models/checkpoint/")"
