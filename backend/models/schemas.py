from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ToolRequest(BaseModel):
    tool_name: str
    input_text: str
