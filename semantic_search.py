import faiss
from transformers import AutoTokenizer, AutoModel
from datasets import Dataset

# Load the pre-trained model and tokenizer
model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = AutoModel.from_pretrained(model_ckpt)

# Define a function for semantic search
def semantic_search(extracted_url, query):
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
