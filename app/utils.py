# my_rag_project/app/utils.py

import os
from PyPDF2 import PdfReader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory # For get_session_history
from langchain_core.chat_history import BaseChatMessageHistory

# Import configuration constants
from app.config import (
    MODEL_NAME, EMBEDDING_MODEL, FAISS_INDEX_PATH, PDF_FILE_PATH, API_KEY
)


def get_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def get_text_chunks(text: str, model_type: str = "Google AI") -> list[str]:
    """Splits a given text into manageable chunks."""
    if model_type == "Google AI":
        chunk_size = 10000
        chunk_overlap = 1000
    else:
        chunk_size = 2000
        chunk_overlap = 200

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks: list[str], api_key: str) -> FAISS:
    """Creates and saves a FAISS vector store from text chunks."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=api_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store

def load_or_create_vector_store(file_path: str, api_key: str, index_path: str) -> FAISS:
    """Loads an existing FAISS vector store or creates a new one if it doesn't exist."""
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=api_key)

    if not os.path.exists(os.path.join(index_path, "index.faiss")) or \
       not os.path.exists(os.path.join(index_path, "index.pkl")):
        print("FAISS index not found. Embedding PDF and creating vector store...")
        pdf_text = get_text_from_pdf(file_path)
        if not pdf_text:
            raise ValueError("Could not extract text from PDF. Cannot create vector store.")
        chunks = get_text_chunks(pdf_text, MODEL_NAME)
        vector_store = get_vector_store(chunks, api_key)
        print("Vector store created and saved.")
    else:
        print("Loading existing FAISS vector store...")
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        print("Vector store loaded.")
    return vector_store

# In-memory store for chat history sessions (accessible by main.py)
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns a ChatMessageHistory object for a given session ID.
    The trimming of messages is handled within the chain's preprocessing.
    """
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]