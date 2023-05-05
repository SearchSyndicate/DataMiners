## sementic search module
from crawl import crawl_se_level
from crawl import crawl
import faiss
from transformers import AutoTokenizer, AutoModel
from datasets import Dataset
from langdetect import detect
from urls_info_retrive import get_url_from_name
from translation import aws_translation


##define module variable
# create a semnetic search function to retrieve most relative urls
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
        lambda x: {"embeddings": get_embeddings(x["urls"]).cpu().detach().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"{query} products and service"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=15)
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
    question = f"what is {query} prdocts ans services? also mention offers don't mention any money."
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=3)

    # Return the search results
    return list(samples["tags"])

# here we define a semantic search over text which in df["tag_text_div"
# input will be the df get out of crawl function 
# Define a function for semantic search
# Define a function for semantic search div data
def semantic_search_div(list_text):
    texts = []
    for text in list_text:
      language = detect(" ".join(text[0:10]))
      if language == "en":
        try:
          texts = texts + text
        except Exception as e:
          continue
    texts = list(set(texts))
    # Convert the extracted url to a dataset
    dict_urls = {"div": texts}
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
    question = f"what that company produce and which pructs it have"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=25)

    # Return the search results
    return list(samples["div"])
def handle_text(tag_text):
   text_to_enc = []
   for sub_text in tag_text:
      text_to_enc.append([" ".join(sub_text)])
   return text_to_enc

query = "IKEA"
start_url = get_url_from_name(query)
extracted_url = crawl(url=start_url)
samples_urls = semantic_search_urls(extracted_url=extracted_url, query=query)
output = crawl_se_level(samples_urls)
text_to_enc = handle_text(output["tag_text_p"])
sample_text = semantic_search_tags(list_text=text_to_enc, query=query)
for smaple in sample_text:
    sample = " ".join(smaple)
    sample = sample.replace("\n", "")
    aws_translation(sample)
    #print(sample.replace("\n", ""))
   
   #print(sample_text)
   #tokenizer.save_vocabulary("/home/muhamad/Search_Engine_competition/DataMiners/models")
   #model.save_pretrained("/home/muhamad/Search_Engine_competition/DataMiners/models")
   # to load tokenizer "tokenizer = AutoTokenizer.from_pretrained("./models/tokenizer/")"
   # load the model "model = AutoModel.from_from_pretrained("./models/checkpoint/")"