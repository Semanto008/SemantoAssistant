# app/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Configuration ---
# Your Google AI API Key - retrieved from environment variable
# On Render, you configure this as an environment variable in the dashboard.
API_KEY = os.getenv("GOOGLE_API_KEY")

# Model and Project Paths
MODEL_NAME = "Google AI"
EMBEDDING_MODEL = "models/embedding-001"
CHAT_MODEL = "gemini-2.5-flash-lite"

# Path to your PDF file relative to the project root (where uvicorn is run from)
PDF_FILE_PATH = "SemantoGhoshGenAIResume.pdf"
FAISS_INDEX_PATH = "faiss_index" # Directory where FAISS index will be saved/loaded

# Chat History Configuration
CHAT_HISTORY_WINDOW_SIZE = 6 # Total number of messages (3 user, 3 AI) for 3 exchanges
