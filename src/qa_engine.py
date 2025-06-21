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

def ask_question(doc_text, user_q, chat_context=None):
    context = f"Previous Q&A (for context):\n{chat_context}\n" if chat_context else ""
    prompt = f"""
{context}You are a research assistant. Answer the user's question based ONLY on the document below. Quote or reference the relevant section/paragraph in your justification. Do NOT make up information.

Document:
{doc_text[:4000]}

Question: {user_q}

Answer (with justification):
"""
    messages = [{"role": "user", "content": prompt}]
    answer = groq_chat_completion(messages, max_tokens=400, temperature=0.2, model="llama3-8b-8192")
    if 'Justification:' in answer:
        parts = answer.split('Justification:')
        return parts[0].strip(), parts[1].strip()
    else:
        return answer, "Justification not found."

def generate_challenges(doc_text):
    prompt = f"""
Generate three logic-based or comprehension-focused questions based ONLY on the document below. The questions should require reasoning or inference, not just fact recall.

Document:
{doc_text[:4000]}

Questions:
1.
"""
    messages = [{"role": "user", "content": prompt}]
    content = groq_chat_completion(messages, max_tokens=300, temperature=0.7, model="llama3-8b-8192")
    questions = [q.strip()[2:].strip() if q.strip().startswith(str(i+1)) else q.strip() for i, q in enumerate(content.split('\n')) if q.strip()]
    if len(questions) < 3:
        questions = [q.strip() for q in content.split('\n') if q.strip()][:3]
    return questions[:3]

def evaluate_answer(doc_text, question, user_answer):
    prompt = f"""
You are a research assistant. Evaluate the user's answer to the question below, using ONLY the document. Provide feedback and a justification referencing the document section/paragraph.

Document:
{doc_text[:4000]}

Question: {question}
User's Answer: {user_answer}

Feedback (with justification):
"""
    messages = [{"role": "user", "content": prompt}]
    feedback = groq_chat_completion(messages, max_tokens=300, temperature=0.3, model="llama3-8b-8192")
    if 'Justification:' in feedback:
        parts = feedback.split('Justification:')
        return parts[0].strip(), parts[1].strip()
    else:
        return feedback, "Justification not found."

def find_snippet(doc_text, justification):
    # Try to find a supporting snippet from the justification in the document
    just = justification.strip().replace('\n', ' ')
    for sent in doc_text.split('\n'):
        if just[:30].lower() in sent.lower():
            return sent.strip()
    # fallback: return first 200 chars of justification if not found
    return just[:200] if just else None 