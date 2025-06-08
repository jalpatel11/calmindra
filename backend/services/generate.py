import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
token = os.getenv("HF_TOKEN")
print("Token loaded:", token is not None)

classifier = InferenceClient("bhadresh-savani/distilbert-base-uncased-emotion", token=token)
client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=token)

def generate_response(message):
    emotion_data = classifier.text_classification(message, top_k=1)
    emotion = emotion_data[0]["label"]
    prompt = (
    f"[INST] You are Calmindra, an empathetic AI assistant trained to support mental health. "
    f"Respond to the user's concern below with a short and supportive message.\n\n"
    f"Concern: {message}\n\nResponse:[/INST]"
)

    print("Prompt:", prompt)
    reply = client.text_generation(prompt, max_new_tokens=200, temperature=0.7, stream=False)
    print("Generated reply:", reply)
    return reply
