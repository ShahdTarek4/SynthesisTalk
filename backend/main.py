from fastapi import FastAPI
from routers import chat, tools

app = FastAPI(title="SynthesisTalk Backend")

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(tools.router, prefix="/tools", tags=["Tools"])

@app.get("/")
def root():
    return {"message": "SynthesisTalk backend is running"}

