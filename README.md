# SynthesisTalk – Collaborative Research Assistant

SynthesisTalk is an intelligent, full-stack AI research assistant that combines conversational reasoning with powerful tool integration. Designed for exploratory research and learning workflows, it supports multi-turn conversations, document summarization, web search, visualization, and export capabilities — all enhanced by Chain-of-Thought (CoT) and ReAct reasoning techniques.

---

## 📚 Table of Contents

1. [Features](#features)  
2. [Project Structure](#project-structure)  
3. [Technologies Used](#technologies-used)  
4. [Setup Instructions](#setup-instructions)  
    - [Backend Setup](#backend-setup)  
    - [Frontend Setup](#frontend-setup)  
5. [Tool Overview](#tool-overview)  
6. [Reasoning Techniques](#reasoning-techniques)  
7. [Note](#Note)  


---

## ✨ Features

- Context-aware, multi-turn chat with LLM integration  
- Chain-of-Thought and ReAct-based reasoning  
- PDF upload and summarization  
- Bullet-point and JSON format summarization  
- Web search with contextual query enhancement  
- Data visualization (bar/pie charts)  
- Persistent note-taking  
- Export conversation to PDF  
- UI built with TailwindCSS and Recharts  

---

## 🗂 Project Structure

```
FinalProject_SynthesisTalk/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── routers/                # Chat and tool routes
│   ├── services/               # Core logic: LLM, tools, context
│   ├── models/                 # Pydantic schemas
│   └── data/                   # User history & notes (JSON)
│   └── exports/                # PDF outputs
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main layout
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── App.css 
│   │   └── components/
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       ├── ContextPanel.jsx
│   │       ├── NotesPanel.jsx
│   │       └── DocumentUploader.jsx
│   └── package.json
```

---

## ⚙️ Technologies Used

- **Frontend**: React, Vite, TailwindCSS, Recharts, Axios  
- **Backend**: FastAPI, Python 3.10+, pdfplumber, ReportLab  
- **LLM API**: NGU LLM Qwen Model/ Groq API 
- **Search**: DuckDuckGo Search API  
- **Storage**: JSON-based conversation and notes persistence  

---

## 🚀 Setup Instructions

1. Clone the Repository
```bash
git clone https://github.com/ShahdTarek4/SynthesisTalk.git
cd SynthesisTalk
```

### 🧩 Backend Setup

1. Navigate to the `/backend` directory:
```bash
cd backend
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. Create a `.env` file with your LLM API credentials:
```env
NGU_API_KEY=your_api_key_here
NGU_BASE_URL=https....
NGU_MODEL=lmodel
```

4. Run the FastAPI backend:
```bash
uvicorn main:app --reload
```

The API will be live at: `http://localhost:8000`

---

### 💻 Frontend Setup

1. Navigate to the `/frontend` directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

> Make sure CORS is enabled for the frontend port in the backend.

---

## 🧪 Tool Overview

| Tool         | Description |
|--------------|-------------|
| `summarize`  | Generates summaries in text, bullets, or JSON |
| `clarify`    | Simplifies complex concepts using CoT |
| `search`     | Performs web search via DuckDuckGo |
| `visualize`  | Extracts key insights and returns chart data |
| `react_agent`| Performs Reason + Action using multiple tools |
| `qa`         | Answers questions using self-corrected CoT |
| `upload`     | Parses and summarizes PDF files |
| `export`     | Converts chat outputs to formatted PDFs |
| `notes`      | Save, delete, and list user notes |

---

## Reasoning Techniques

- **Chain-of-Thought (CoT)**  
  Prompts the model to answer step-by-step, improving accuracy and interpretability. Used in summarization, QA, and clarify tools.

- **ReAct (Reason + Act)**  
  Combines reasoning with dynamic tool invocation. The LLM produces Thought → Action → Observation → Final Answer structures and executes tools via the backend.

- **Context Management**  
  Uses recent 10 messages for coherence. Special logic in `context_manager.py` ensures context relevancy per tool type (e.g., search vs. summarize).

---

## ⚠️ Note

- Rate limiting from DuckDuckGo may occur on repeated searches. Use shorter, more specific queries.
- Large PDFs may be truncated to 2000 characters in summary due to API token limits.
- ReAct loops are constrained to 1 step per invocation to prevent infinite cycles.

---


---
