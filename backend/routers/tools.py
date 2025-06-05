# tools.py - FIXED VERSION (Key sections)
from pathlib import Path
from fastapi import APIRouter, Form, UploadFile, File, Request
from models.schemas import ToolRequest
from services import tool_manager, note_manager, document_parser, reasoning, history_manager
from services.context_manager import ContextManager
import os
router = APIRouter()

# Initialize context manager
context_mgr = ContextManager()

@router.post("/use")
def use_tool(tool: ToolRequest):
    """
    FIXED: Enhanced context management for all tools, especially search
    """
    # Get conversation history
    history = history_manager.get_history(tool.user_id) if tool.user_id else []
   
    # Format input appropriately for each tool
    formatted_input = context_mgr.format_tool_input(history, tool.input_text, tool.tool_name)
   
    # Prepare context messages for LLM calls
    context_messages = context_mgr.prepare_context_for_llm(history, formatted_input, tool.tool_name)
   
    # FIXED: Pass history to tool manager for context-aware execution
    result = tool_manager.run_tool_with_context(tool.tool_name, formatted_input, context_messages, history)
    
    # Save to history consistently
    if tool.user_id:
        # Save user's original input (not the formatted version)
        history_manager.add_message(tool.user_id, tool.input_text)
       
        # Save assistant's response
        if isinstance(result, str):
            history_manager.add_message(tool.user_id, result)
        elif isinstance(result, dict):
            # For structured results, save a readable version
            if "result" in result:
                history_manager.add_message(tool.user_id, str(result["result"]))
            elif tool.tool_name == "visualize":  # Special case for visualization
                history_manager.add_message(tool.user_id, "Generated visualization chart from research data")
            else:
                history_manager.add_message(tool.user_id, f"Completed {tool.tool_name} operation")

    return {"result": result}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = Form(...)):
    """
    Enhanced upload supporting PDF and Word documents
    """
    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    
    # Validate file type
    supported_extensions = ['.pdf', '.docx', '.doc']
    if file_extension not in supported_extensions:
        return {
            "error": f"Unsupported file type. Supported formats: {', '.join(supported_extensions)}",
            "filename": file.filename
        }
    
    # Save uploaded file
    file_path = f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text based on file type
        content = document_parser.extract_text_from_document(file_path, file_extension)
        
        # Check if extraction was successful
        if content.startswith("Error"):
            return {
                "error": content,
                "filename": file.filename
            }
        
        # Generate summary
        summary = reasoning.chain_of_thought_summary(content[:2000])
        
        # Determine file icon based on type
        file_icon = "📄" if file_extension == '.pdf' else "📝"
        
        # Save to conversation history
        summary_message = f"{file_icon} Uploaded **{file.filename}**\n\n📝 Summary:\n{summary}"
        history_manager.add_message(user_id, summary_message)
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            "filename": file.filename,
            "file_type": file_extension,
            "extracted_content": content[:500] + "..." if len(content) > 500 else content,
            "summary": summary,
            "success": True
        }
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            "error": f"Failed to process {file.filename}: {str(e)}",
            "filename": file.filename
        }
    

@router.post("/note/save")
def save_note(user_id: str = Form(...), note: str = Form(...)):
    return note_manager.save_note(user_id, note)

@router.get("/note/list")
def list_notes(user_id: str):
    return note_manager.get_notes(user_id)

@router.post("/note/delete")
def delete_note(user_id: str = Form(...), index: int = Form(...)):
    return note_manager.delete_note(user_id, index)

@router.post("/note/clear")
def clear_notes(user_id: str = Form(...)):
    return note_manager.clear_notes(user_id)

@router.post("/visualize")
def visualize_tool(tool: ToolRequest):
    # Get conversation history
    history = history_manager.get_history(tool.user_id) if tool.user_id else []
    
    # Format input appropriately for visualization
    formatted_input = context_mgr.format_tool_input(history, tool.input_text, "visualize")
    
    # Prepare context messages
    context_messages = context_mgr.prepare_context_for_llm(history, formatted_input, "visualize")
    
    # Run tool with context
    result = tool_manager.run_tool_with_context("visualize", formatted_input, context_messages)
    
    return {"chart_data": result}

@router.post("/react_agent")
def use_react_agent(tool: ToolRequest):
    # Get conversation history
    history = history_manager.get_history(tool.user_id) if tool.user_id else []
    
    # Format input
    formatted_input = context_mgr.format_tool_input(history, tool.input_text, "react_agent")
    
    # Prepare context messages
    context_messages = context_mgr.prepare_context_for_llm(history, formatted_input, "react_agent")
    
    # Run tool with context
    result = tool_manager.run_tool_with_context("react_agent", formatted_input, context_messages)
    
    return {"result": result}

@router.post("/export")
def export_as_pdf(tool: ToolRequest):
    # Get conversation history
    history = history_manager.get_history(tool.user_id) if tool.user_id else []
    
    # Format input
    formatted_input = context_mgr.format_tool_input(history, tool.input_text, "export_pdf")
    
    # Prepare context messages
    context_messages = context_mgr.prepare_context_for_llm(history, formatted_input, "export_pdf")
    
    # Run tool with context
    result = tool_manager.run_tool_with_context("export_pdf", formatted_input, context_messages)
    
    return {"result": result}

@router.post("/qa")
def qa_tool(tool: ToolRequest):
    # Get conversation history
    history = history_manager.get_history(tool.user_id) if tool.user_id else []
    
    # Format input
    formatted_input = context_mgr.format_tool_input(history, tool.input_text, "qa")
    
    # Prepare context messages
    context_messages = context_mgr.prepare_context_for_llm(history, formatted_input, "qa")
    
    # Run tool with context
    result = tool_manager.run_tool_with_context("qa", formatted_input, context_messages)
    
    return {"result": result}

@router.post("/convo/reset")
async def reset_conversation(request: Request):
    body = await request.json()
    user_id = body.get("user_id")
    if not user_id:
        return {"error": "Missing user_id"}

    history_manager.clear_history(user_id)
    return {"status": "conversation reset"}

# Add this to your tools.py file

@router.post("/generate_topic")
def generate_topic_title(request: dict):
    """
    Generate a conversation topic title without saving to history
    """
    conversation_text = request.get("conversation_text", "")
    
    if not conversation_text:
        return {"topic": "New Conversation"}
    
    # Create a focused prompt for topic generation
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a topic summarizer. Generate a concise 3-5 word title "
                "that captures the main research topic or question being discussed. "
                "Return only the title, no quotes, no extra text."
            )
        },
        {
            "role": "user", 
            "content": f"Generate a topic title for this conversation:\n\n{conversation_text}"
        }
    ]
    
    try:
        response = reasoning.call_llm_with_messages(messages)
        
        # Clean up the response
        topic = response.strip()
        topic = topic.replace('"', '').replace("'", "")
        topic = topic.replace("Title:", "").strip()
        
        # Ensure it's not too long
        if len(topic) > 50:
            words = topic.split()[:4]  # Take first 4 words
            topic = " ".join(words)
        
        return {"topic": topic if topic else "Research Discussion"}
        
    except Exception as e:
        print(f"Topic generation error: {e}")
        return {"topic": "Research Discussion"}