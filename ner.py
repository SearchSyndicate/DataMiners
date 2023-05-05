from semantic_search import text_to_enc

import spacy

# Load the pre-trained model
nlp = spacy.load("en_core_web_sm")

# Define the text to be analyzed
text = "Apple is looking at buying U.K. startup for $1 billion"

# Analyze the text using the loaded model
doc = nlp(text)

# Print the detected named entities and their labels
for ent in doc.ents:
    print(ent.text, ent.label_)
