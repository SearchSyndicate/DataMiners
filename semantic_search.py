## sementic search module
from crawl import crawl
from urls_info_retrive import get_url_from_name
import faiss
from transformers import AutoTokenizer, AutoModel
from datasets import Dataset
from langdetect import detect

## return data from crawl function 
query = "IKEA"
start_url = get_url_from_name(query)
visited_url, output = crawl(url=start_url)


# Load the pre-trained model and tokenizer
model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = AutoModel.from_pretrained(model_ckpt)


# this function to extract  the most related urls which i will use later with semantic search over text for the next two function
# Define a function for semantic search
# input will be the extracted_url from crawl fucntion + the input query (company name)

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
        lambda x: {"embeddings": get_embeddings(x["urls"]).detach().cpu().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"{query} products and service"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=5)

    # Return the search results
    return list(samples["urls"])




# here we define a semantic search over text which in df["tag_text_p"
# input will be the df get out of crawl function 
# Define a function for semantic search
def semantic_search_tags(list_text):
    texts = []
    for text in list_text[0:100]:
      language = detect(" ".join(text[0:10]))
      if language == "en":
        try:
          texts = texts + text
        except Exception as e:
          continue
    texts = list(set(texts))
    # Convert the extracted url to a dataset
    dict_urls = {"tags": texts}
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
        lambda x: {"embeddings": get_embeddings(x["tags"]).detach().cpu().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"what that company produce and which pructs it have"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=25)

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
        lambda x: {"embeddings": get_embeddings(x["div"]).detach().cpu().numpy()[0]}
    )
    embeddings_dataset.add_faiss_index(column="embeddings")

    # Search for similar URLs
    question = f"what that company produce and which pructs it have"
    question_embedding = get_embeddings([question]).cpu().detach().numpy()
    scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=25)

    # Return the search results
    return list(samples["div"])

if __name__ == "__main__":
   samples_urls = semantic_search_urls(extracted_url=output["url"], query=query)
   sample_text = semantic_search_tags(list_text = output["tag_text_p"])