# my_rag_project/app/models/chat.py

from pydantic import BaseModel

class UserQuery(BaseModel):
    """
    Pydantic model for incoming user questions.
    """
    session_id: str
    question: str

# You might add a response model if your response is more complex
# class AssistantResponse(BaseModel):
#     answer: str
#     # Optional: source_documents: List[Dict]