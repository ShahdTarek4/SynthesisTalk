from fastapi import APIRouter
from models.schemas import ToolRequest
from services import tool_manager
from services import note_manager
from fastapi import Form
from fastapi import UploadFile, File
from services import document_parser, reasoning
from services import tool_manager, history_manager

from fastapi import UploadFile, File
from services import document_parser, reasoning



router = APIRouter()

@router.post("/use")
def use_tool(tool: ToolRequest):
    input_text = tool.input_text

    # Prepend chat history if available
    if tool.user_id:
        history = history_manager.get_history(tool.user_id)
        if history:
            context = "\n".join(history[-10:])  # get last 10 messages max
            input_text = f"Conversation so far:\n{context}\n\nNow: {input_text}"

    return {"result": tool_manager.run_tool(tool.tool_name, input_text)}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    content = document_parser.extract_text_from_pdf(file_path)
    summary = reasoning.chain_of_thought_summary(content[:2000])

    return {
        "filename": file.filename,
        "extracted_content": content[:500] + "...",
        "summary": summary
    }


@router.post("/note/save")
def save_note(user_id: str = Form(...), note: str = Form(...)):
    return note_manager.save_note(user_id, note)

@router.get("/note/list")
def list_notes(user_id: str):
    return note_manager.get_notes(user_id)

@router.post("/visualize")
def visualize_tool(tool: ToolRequest):
    return {"chart_data": tool_manager.run_tool("visualize", tool.input_text)}

@router.post("/react_agent")
def use_react_agent(tool: ToolRequest):
    return {"result": tool_manager.run_tool("react_agent", tool.input_text)}

@router.post("/export")
def export_as_pdf(tool: ToolRequest):
    return {"result": tool_manager.run_tool("export_pdf", tool.input_text)}
