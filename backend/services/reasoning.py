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

You must return exactly one complete reasoning cycle, consisting of:
1. Thought: What you need to consider
2. Action: Use one of the following tools - Search[], Clarify[], or Summarize[]
3. Observation: Show what you found
4. Final Answer: Conclude based on your observation

Only return this exact structure. Do NOT loop. Do NOT repeat the cycle.
Use one tool. End with a Final Answer.

Only use the above tools. Do not invent tools.

Example:

Thought: I should search for benefits of AI in education.
Action: Search["benefits of AI in education"]
Observation: AI helps with personalization, grading automation, accessibility...
Final Answer: The key benefits of AI in education are personalization, automation, and accessibility.
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

def call_llm_with_messages(messages): #for React and context-aware responses
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
        print("Context-aware LLM Error:", e)
        return "Error: Failed to get response from LLM."

def chain_of_thought_summary(text, format="text"): #backend
    if format == "JSON":
        prompt = f"Summarize the following text as raw JSON only. Do not include markdown formatting or code blocks. Just output a valid JSON object.\n\n{text}"
    elif format == "bullets":
        prompt = f"Summarize the following text using concise bullet points:\n\n{text}"
    else:
        prompt = f"Let's think step by step. Summarize this logically:\n\n{text}"

    return call_llm(prompt)

def chain_of_thought_answer(question):  #backend
    prompt = f"Let's think step by step. Answer this question logically:\n{question}"
    return self_corrected_response(prompt) # self-correction



def clarify_concept_enhanced(context_messages):
    """
    Enhanced clarification with educational focus - maintains full context
    """
    clarify_prompt = """

CLARIFICATION MODE: You are now acting as a helpful teacher. When clarifying concepts:

1. Define key terms clearly
2. Explain step-by-step how things work  
3. Use simple analogies or examples
4. Break complex ideas into parts
5. Connect to our conversation context

Be educational and help the user truly understand the concept.
"""
    
    # Update system message while preserving all context
    enhanced_messages = context_messages.copy()
    enhanced_messages[0]['content'] += clarify_prompt
    
    # Use the same context-aware function with enhanced prompt
    return call_llm_with_messages(enhanced_messages)

# FIXED: Use consistent context management
def respond_with_context(messages):
    """
    Respond using properly formatted messages with context
    """
    try:
        response = call_llm_with_messages(messages)
        return response
    except Exception as e:
        print("Context-aware LLM Error:", e)
        return "Sorry, I couldn't generate a response due to a context error."



def generate_visual_data(text): 
    """
    Improved function to generate relevant visualization data from research text.
    Just replace your existing function with this one.
    """
    
    # Better prompt that focuses on the actual content
    prompt = f"""
Analyze this research content and identify the 4-6 most important topics or themes discussed.

For each topic, provide:
- A specific label based on what's actually discussed (not generic terms)
- A relevance score from 1-10 based on how much it's mentioned or emphasized

Research content to analyze:
{text}

Return ONLY a JSON array in this exact format:
[
  {{"label": "Specific Topic Name", "count": 8}},
  {{"label": "Another Actual Topic", "count": 6}},
  {{"label": "Third Real Topic", "count": 4}}
]

Make sure the labels reflect what's actually in the text, not generic research terms.
"""

    try:
        raw_output = call_llm(prompt)
        print("LLM raw output:", raw_output)

        # Better JSON extraction - try multiple patterns
        # Pattern 1: Full array
        match = re.search(r'\[\s*\{.*?\}\s*\]', raw_output, flags=re.DOTALL)
        if match:
            cleaned = match.group(0).strip()
        else:
            # Pattern 2: Find individual objects and combine
            objects = re.findall(r'\{[^}]*"label"[^}]*"count"[^}]*\}', raw_output)
            if objects:
                cleaned = '[' + ','.join(objects) + ']'
            else:
                # Fallback
                cleaned = '[{"label": "Analysis Error", "count": 1}]'

        print("Cleaned for JSON:", cleaned)
        
        # Parse and validate
        data = json.loads(cleaned)
        
        # Clean up the data
        cleaned_data = []
        for item in data:
            if isinstance(item, dict) and 'label' in item and 'count' in item:
                label = str(item['label']).strip()
                # Truncate long labels
                if len(label) > 25:
                    label = label[:22] + "..."
                
                # Ensure count is a positive number
                try:
                    count = max(1, int(item['count']))
                except:
                    count = 1
                
                cleaned_data.append({"label": label, "count": count})
        
        # Return up to 6 items
        return cleaned_data[:6] if cleaned_data else [{"label": "No Topics Found", "count": 1}]
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return [{"label": "Parsing Error", "count": 1}]
    except Exception as e:
        print(f"Error generating visual data: {e}")
        return [{"label": "Processing Error", "count": 1}]

def run_full_react(question):
    messages = [
        {"role": "system", "content": react_system_message},
        {"role": "user", "content": question}
    ]

    # Step 1: Get initial Thought + Action + Observation structure
    response = call_llm_with_messages(messages)

    # Step 2: Extract the action
    action_match = re.search(r"Action:\s*(\w+)\[([^\]]+)\]", response)
    if not action_match:
        return response

    tool_name = action_match.group(1).strip().lower()
    input_text = action_match.group(2).strip()

    if tool_name == "search":
        tool_result = search.search_web(input_text)
        
        # Handle different return types from search
        if isinstance(tool_result, str):
            # If search returns a string summary, use it directly
            obs_text = tool_result
        elif isinstance(tool_result, list) and tool_result:
            # If search returns a list of dictionaries
            obs_text = "\n".join(
                f"- {r.get('title', 'No title')}: {r.get('body', 'No content')[:200]}" 
                for r in tool_result[:3] if isinstance(r, dict)
            )
        else:
            obs_text = "No search results found"
            
    elif tool_name == "clarify":
        obs_text = chain_of_thought_summary(f"Explain this clearly:\n{input_text}")
    elif tool_name == "summarize":
        obs_text = chain_of_thought_summary(input_text)
    else:
        obs_text = f"Unknown tool: {tool_name}"

    # Step 3: Inject the real observation
    full_trace = re.sub(
        r"Observation:.*", f"Observation: {obs_text}", response, flags=re.DOTALL
    )

    # Step 4: If Final Answer already exists, return trace
    if "Final Answer:" in full_trace:
        return full_trace

    # Step 5: Otherwise, ask LLM for Final Answer
    followup_prompt = (
        f"{full_trace}\n\nNow provide a Final Answer based on the above observation."
    )
    final_response = call_llm(followup_prompt)

    # Combine everything
    return f"{full_trace}\n\nFinal Answer: {final_response.strip()}"

# REMOVED: format_history_as_dialogue 

def self_corrected_response(prompt: str, max_attempts=2):
    initial = call_llm(prompt)
    print(" Initial answer:\n", initial)

    evaluation_prompt = f"""Evaluate the following answer. Is it vague, incomplete, or unclear? Reply "yes" or "no".\n\nAnswer:\n{initial}"""
    eval_result = call_llm(evaluation_prompt).strip().lower()
    print("Evaluation result for initial answer:", eval_result)

    if "no" in eval_result:
        print("Initial answer accepted.")
        return initial

    for attempt in range(max_attempts):
        retry_prompt = f"""The previous response was not helpful. Please try again using clearer and more detailed reasoning:\n{prompt}"""
        revised = call_llm(retry_prompt)
        print(f"Retry #{attempt+1} revised answer:\n", revised)

        evaluation_prompt = f"""Evaluate the following revised answer. Is it vague or incomplete? Reply "yes" or "no".\n\nAnswer:\n{revised}"""
        eval_result = call_llm(evaluation_prompt).strip().lower()
        print(" Evaluation result for retry:", eval_result)

        if "no" in eval_result:
            print("Revised answer accepted.")
            return revised
        
    print(" All retries evaluated as vague. Returning latest retry.")
    return revised  # fallback to latest if no improvement