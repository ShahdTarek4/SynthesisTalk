import os
import requests
from dotenv import load_dotenv
from collections import Counter
import re
from services import search
import json 

load_dotenv()

API_KEY = os.getenv("NGU_API_KEY")
BASE_URL = os.getenv("NGU_BASE_URL")
MODEL = os.getenv("NGU_MODEL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

#Prompting LLM for ReAct 
react_system_message = """
You are a helpful research assistant using the ReAct (Reasoning + Acting) approach.

When responding to questions, follow this pattern:
1. Thought: Think about what you need to know
2. Action: Use a tool (Search[], Clarify[], Summarize[])
3. Observation: Review the tool result
... (repeat as needed)
Final Answer: Provide a conclusive answer.

You may only use these tools:
- Search[query]: to search the web
- Clarify[text]: to simplify content
- Summarize[text]: to summarize a passage

Always show your reasoning steps and tool usage.

Example:
User: What are the benefits of AI in education?

Thought: I should find real examples of AI in education.
Action: Search["benefits of AI in education"]
Observation: AI helps personalize learning, automate grading...
Thought: Now I can summarize the main benefits.
Final Answer: The key benefits of AI in education are...

You MUST use at least one of the tools (Search[], Clarify[], Summarize[]) before giving a Final Answer.
Do NOT answer directly without using a tool.
Only use the above tools. Do not invent tools.
"""



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

def call_llm_with_messages(messages): #for React
    url = f"{BASE_URL}/chat/completions"
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("ReAct error:", e)
        return "Error: Failed to get response from LLM."
    

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
        "messages": messages[-10:],  
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(" Context-aware LLM Error:", e)
        return "Sorry, I couldn't generate a response due to a context error."
    


def generate_visual_data(text):
    prompt = (
        "Extract and return the top 5 key themes or topics from the following research text. "
        "Return them as a JSON array of objects like: [{ \"label\": \"topic\", \"count\": 3 }]. Do not include extra text or markdown. Only output raw JSON.\n\n"
        + text
    )
    raw_output = call_llm(prompt)
    print(" LLM returned:", raw_output)

    # Remove Markdown formatting like ```json
    cleaned = re.sub(r"```(?:json)?", "", raw_output).replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print(" Failed to parse JSON.")
        return [{"label": "Parsing Error", "count": 1}]
    

def run_full_react(question):
    messages = [
        {"role": "system", "content": react_system_message},
        {"role": "user", "content": question}
    ]

    for _ in range(5):  # limit loops to avoid infinite cycles
        # Step 1: Call the LLM
        response = call_llm_with_messages(messages)
        messages.append({"role": "assistant", "content": response})

        # Step 2: Parse Action from response
        action_match = re.search(r"Action:\s*(\w+)\[([^\]]+)\]", response)
        if action_match:
            tool_name = action_match.group(1).strip().lower()
            input_text = action_match.group(2).strip()

            # Step 3: Execute the tool
            if tool_name == "search":
                tool_result = search.search_web(input_text)
                obs_text = "\n".join(f"- {r['title']}: {r['body'][:200]}" for r in tool_result[:3])
            elif tool_name == "clarify":
                obs_text = chain_of_thought_summary(f"Explain this clearly:\n{input_text}") #use COT for observation stage of react
            elif tool_name == "summarize":
                obs_text = chain_of_thought_summary(input_text)
            else:
                obs_text = f"Unknown tool: {tool_name}"

            # Step 4: Feed Observation back to LLM
            messages.append({"role": "user", "content": f"Observation: {obs_text}"})

        elif "Final Answer:" in response:
            # We’re done
            return response

    return "❌ ReAct loop ended without a final answer."