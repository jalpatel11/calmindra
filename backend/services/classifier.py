import os
from huggingface_hub import InferenceClient

classifier = InferenceClient("bhadresh-savani/distilbert-base-uncased-emotion", token=os.getenv("HF_TOKEN"))

def classify_emotion(text):
    response = classifier.text_classification(text, top_k=1)
    return response[0]["label"]
