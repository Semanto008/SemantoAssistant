# my_rag_project/app/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "Google AI"
EMBEDDING_MODEL = "models/embedding-001"
CHAT_MODEL = "gemini-2.5-flash-lite"
PDF_FILE_PATH = "app/SemantoGhoshGenAIResume.pdf" # Ensure this path is correct relative to where you run uvicorn
FAISS_INDEX_PATH = "faiss_index"
CHAT_HISTORY_WINDOW_SIZE = 6 # Total number of messages (3 user, 3 AI) for 3 exchanges