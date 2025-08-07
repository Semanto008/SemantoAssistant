# Semanto's AI Assistant
This project is a conversational AI assistant designed to answer questions based on the professional profile of Semanto Ghosh. It uses a Retrieval Augmented Generation (RAG) pipeline built with LangChain, a FastAPI backend to serve the API, and a FAISS vector store for efficient document searching.

The application can process a PDF resume, create a searchable knowledge base, and answer questions conversationally while retaining memory of the last few interactions.

Features
PDF Processing: Reads and extracts text from a PDF resume.

Knowledge Base: Creates a FAISS vector store from the resume content for fast semantic search.

Conversational Memory: Uses LangChain's RunnableWithMessageHistory to remember the context of the last few conversation turns, enabling natural follow-up questions.

FastAPI Backend: Exposes a single /ask API endpoint for a frontend to communicate with.

Modular Architecture: The codebase is structured for clarity and maintainability, separating concerns into different modules (config, utils, chains, models).


How to Run Locally
Follow these steps to get a local copy of the project up and running.

1. Prerequisites
Python 3.8+ installed.

pip for installing packages.

2. Setup the Environment
Clone the repository:

git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

(Replace with your GitHub details)

Create a virtual environment and activate it:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

3. Set up API Key
Create a file named .env in the root of your project directory and add your Google AI API key:

.env

GOOGLE_API_KEY="YOUR_ACTUAL_GOOGLE_API_KEY_HERE"

Warning: The .env file should not be committed to a public repository. It is included in the .gitignore file by default for this reason.

4. Prepare the Knowledge Base
The project relies on a pre-built FAISS index for document retrieval.

Place the SemantoGhoshGenAIResume.pdf file in the root of the project directory.

The first time you run the application, it will automatically create the faiss_index/ directory and its contents. To ensure this works, run the load_or_create_vector_store function locally by either running a local test script or, if you've already tried running the FastAPI server locally, it should have been created. If not, follow the Run the Backend step below, and the server's startup routine will create it.

5. Run the Backend
Start the FastAPI server using uvicorn from your terminal. Make sure you are in the project's root directory and your virtual environment is active.

uvicorn app.main:app --host 0.0.0.0 --port 8000

The server will now be running and accessible at http://127.0.0.1:8000.

6. Frontend Integration
Your backend API is now live and ready to be connected to a frontend.

API Endpoint: http://127.0.0.1:8000/ask (for local development)

Request Method: POST

Request Body: {"session_id": "string", "question": "string"}

Response Body: {"answer": "string"}
