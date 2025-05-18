import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NGU_API_KEY")
BASE_URL = os.getenv("NGU_BASE_URL")
MODEL = os.getenv("NGU_MODEL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def chain_of_thought_summary(text, format="text"):
    if format == "JSON":
        prompt = f"Summarize the following text as raw JSON only. Do not include markdown formatting or code blocks. Just output a valid JSON object.\n\n{text}"
    elif format == "bullets":
        prompt = f"Summarize the following text using concise bullet points:\n\n{text}"
    else:
        prompt = f"Let's think step by step. Summarize this logically:\n\n{text}"

    return call_llm(prompt)


def chain_of_thought_answer(question):
    prompt = f"Let's think step by step. Answer this question logically:\n{question}"
    return call_llm(prompt)

def call_llm(prompt):
    url = f"{BASE_URL}/chat/completions"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(" NGU LLM Error:", e)
        return "Error: Failed to get response from LLM."

def respond_with_history(history):
    url = f"{BASE_URL}/chat/completions"
    messages = []

    # Convert stored strings into alternating user/assistant messages
    for i, msg in enumerate(history):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": msg})

    # Add prompt guidance 
    messages.append({
        "role": "system",
        "content": "You are a helpful and intelligent AI research assistant. Always respond based on prior full conversation context. Use step-by-step reasoning where helpful."
    })

    payload = {
        "model": MODEL,
        "messages": messages[-10:],  # limit to last few to stay under token budget
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(" Context-aware LLM Error:", e)
        return "Sorry, I couldn't generate a response due to a context error."

