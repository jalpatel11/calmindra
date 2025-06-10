import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load Hugging Face token
load_dotenv()
token = os.getenv("HF_TOKEN")
# print("Token loaded:", token is not None)

# Set up clients
classifier = InferenceClient("bhadresh-savani/distilbert-base-uncased-emotion", token=token)
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=token)

def generate_response(message: str):
    emotion_data = classifier.text_classification(message, top_k=1)
    label = emotion_data[0]["label"]
    score = emotion_data[0]["score"]

    if label in {"joy", "neutral"} or score < 0.8:
        prompt = f"[INST] You are Calmindra, a helpful, respectful assistant. Respond concisely to: {message} [/INST]"
    else:
        prompt = f"[INST] You are Calmindra, an empathetic AI assistant trained to support mental health. The user is feeling {label}. Respond supportively to: {message} [/INST]"

    response = client.text_generation(prompt, max_new_tokens=200, temperature=0.7, stream=False)
    return response
