from fastapi import FastAPI
from routers import chat, tools
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware #for connection with frontend 
import os


app = FastAPI(title="SynthesisTalk Backend")
if not os.path.exists("exports"):
    os.makedirs("exports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/exports", StaticFiles(directory="exports"), name="exports")

app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(tools.router, prefix="/tools", tags=["Tools"])

@app.get("/")
def root():
    return {"message": "SynthesisTalk backend is running"}

