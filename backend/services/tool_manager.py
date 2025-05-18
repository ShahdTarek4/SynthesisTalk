from services import reasoning
from services import search


def run_tool(tool_name: str, input_text: str):
    if tool_name == "summarize":
        return reasoning.chain_of_thought_summary(input_text)
    elif tool_name == "qa":
        return reasoning.chain_of_thought_answer(input_text)
    elif tool_name == "search":
        return search.search_web(input_text)
    elif tool_name == "clarify":
        return reasoning.chain_of_thought_summary(f"Can you clarify this for a beginner:\n{input_text}")
    elif tool_name == "summarize_json":
        return reasoning.chain_of_thought_summary(input_text, format="JSON")

    elif tool_name == "summarize_bullets":
        return reasoning.chain_of_thought_summary(input_text, format="bullets")

    else:
        return {"error": "Invalid tool name"}




