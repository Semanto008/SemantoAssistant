# my_rag_project/app/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import (
    API_KEY, MODEL_NAME, EMBEDDING_MODEL, CHAT_MODEL,
    PDF_FILE_PATH, FAISS_INDEX_PATH, CHAT_HISTORY_WINDOW_SIZE
)
from app.utils import load_or_create_vector_store, get_session_history
from app.chains.rag_chain import get_conversational_chain_with_memory
from app.models.chat import UserQuery # Import the Pydantic model

from langchain_core.runnables.history import RunnableWithMessageHistory


# --- Initialize FastAPI app ---
app = FastAPI(
    title="Semanto's AI Assistant",
    description="An AI assistant for answering questions based on Semanto Ghosh's professional profile.",
    version="1.0.0",
)

# --- CORS Middleware ---
# Configure CORS to allow communication from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Replace with your Lovable frontend's URL(s)
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"], # Allow all headers
)

# --- Global Components ---
# These will be initialized once on application startup
db = None
conversational_rag_chain = None

# --- FastAPI Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    Initialize the vector store and the RAG chain when the FastAPI app starts up.
    This ensures they are loaded only once.
    """
    global db, conversational_rag_chain
    try:
        print("Initializing LangChain backend...")
        db = load_or_create_vector_store(PDF_FILE_PATH, API_KEY, FAISS_INDEX_PATH)
        core_rag_chain = get_conversational_chain_with_memory(MODEL_NAME, vectorstore=db, api_key=API_KEY)
        conversational_rag_chain = RunnableWithMessageHistory(
            core_rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )
        print("LangChain backend initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize LangChain backend: {e}")
        # In a production app, you might raise an exception or log and exit.
        # For now, allow app to start but API calls will fail.

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "Welcome to Semanto's AI Assistant API. Use /docs for API documentation."}

@app.post("/ask")
async def ask_assistant(query: UserQuery):
    """
    API endpoint to receive user questions and return assistant's answers.
    """
    if conversational_rag_chain is None:
        raise HTTPException(
            status_code=503,
            detail="AI Assistant not initialized yet. Please try again later."
        )

    try:
        response = conversational_rag_chain.invoke(
            {"input": query.question},
            config={"configurable": {"session_id": query.session_id}}
        )
        return {"answer": response.get("output", "Sorry, I couldn't generate an answer.")}
    except Exception as e:
        print(f"Error processing query for session {query.session_id}: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")