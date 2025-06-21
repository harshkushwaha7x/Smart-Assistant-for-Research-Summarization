from dotenv import load_dotenv
load_dotenv()
import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_chat_completion(messages, max_tokens=300, temperature=0.5, model="llama3-8b-8192"):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def summarize_document(text):
    prompt = (
        "Summarize the following document in no more than 150 words.\n\n" + text[:4000]
    )
    messages = [{"role": "user", "content": prompt}]
    return groq_chat_completion(messages, max_tokens=300, temperature=0.5, model="llama3-8b-8192") 