# tool_manager.py - FIXED VERSION

from services import reasoning
from services import search
from services import export

def run_tool_with_context(tool_name: str, input_text: str, context_messages: list, history: list = None):
    """
    Context-aware tool execution with enhanced search handling
    """
    if tool_name == "summarize":
        # FIXED: Always use context management for summarize
        lowered = input_text.lower()
        
        # If no actual content provided, use last assistant message
        if len(input_text.strip()) < 10 and history:
            last_assistant = [msg for i, msg in enumerate(history) if i % 2 == 1]
            if last_assistant:
                input_text = last_assistant[-1]  # Most recent assistant message
                # Update the context messages with the new input
                context_messages[-1]['content'] = input_text
        
        # Modify system message based on format request
        if "bullet" in lowered:
            # Update system message for bullet format
            context_messages[0]['content'] += "\n\nProvide your summary using concise bullet points."
        elif "json" in lowered or "structured" in lowered or "machine readable" in lowered:
            # Update system message for JSON format  
            context_messages[0]['content'] += "\n\nProvide your summary as raw JSON only. Do not include markdown formatting or code blocks. Just output a valid JSON object."
        else:
            # Default summary format with context
            context_messages[0]['content'] += "\n\nProvide a clear, well-structured summary using the conversation context."
        
        # Always use context-aware response
        return reasoning.respond_with_context(context_messages)

    elif tool_name == "qa":
         initial_response = reasoning.respond_with_context(context_messages)
         return reasoning.self_corrected_response(f"The following is a draft response. Improve it if it is vague or unclear:\n\n{initial_response}")
    
    elif tool_name == "search":
        # FIXED: Enhanced search with conversation context
        context_summary = ""
        if history and len(history) > 0:
            # Extract context for search
            from services.context_manager import ContextManager
            context_mgr = ContextManager()
            context_summary = context_mgr.get_conversation_summary(history)
        
        return search.search_web(input_text, summarize=True, context_summary=context_summary)

    elif tool_name == "clarify":
        
        return reasoning.clarify_concept_enhanced(context_messages)

    elif tool_name == "visualize":
        return reasoning.generate_visual_data(input_text)

    elif tool_name == "react_agent":
        return reasoning.run_full_react(input_text)

    elif tool_name == "export_pdf":
        path = export.generate_pdf(input_text)
        return {"file_path": path}

    else:
        return {"error": "Invalid tool name"}