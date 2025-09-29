# app/main.py

import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

# --- New Imports ---
# We need these message objects to format the chat history correctly for LangChain
from langchain_core.messages import AIMessage, HumanMessage

# Import our conversational engine
from .engine import RagEngine

# Define the path for storing uploaded files.
ABS_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ABS_PATH, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


# --- Pydantic Models for API Data Validation ---

class ChatHistory(BaseModel):
    role: str = Field(..., description="The role of the speaker, e.g., 'user' or 'assistant'")
    content: str = Field(..., description="The content of the message")

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's current question")
    # The chat_history is now correctly typed as a list of our ChatHistory model
    chat_history: Optional[List[ChatHistory]] = Field(None, description="The history of the conversation")


# --- FastAPI Application Setup ---

app = FastAPI(
    title="Intelli-Doc API",
    description="An API for chatting with your documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RagEngine()


# --- API Endpoints ---

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})
    
    file_path = os.path.join(DATA_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        engine.add_document(file_path)
        return {"filename": file.filename, "status": "Successfully uploaded and processed."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to process file: {e}"})


# --- CORRECTED CHAT ENDPOINT ---
@app.post("/chat/")
async def chat_with_doc(request: ChatRequest):
    """
    Endpoint to handle chat requests. It now correctly formats the
    chat history before passing it to the RAG engine.
    """
    try:
        # Convert the list of Pydantic models to a list of LangChain message objects
        formatted_chat_history = []
        if request.chat_history:
            for msg in request.chat_history:
                if msg.role == "user":
                    formatted_chat_history.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    formatted_chat_history.append(AIMessage(content=msg.content))

        result = engine.ask_question(request.question, formatted_chat_history)
        return result
    except Exception as e:
        # Be sure to return the actual error for debugging
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def read_root():
    return {"message": "Welcome to the Intelli-Doc API. Go to /docs to see the documentation."}