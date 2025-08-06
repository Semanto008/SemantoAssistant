from pydantic import BaseModel

class UserQuery(BaseModel):
    """
    Pydantic model for incoming user questions via the API.
    """
    session_id: str # Unique identifier for the conversation session
    question: str   # The actual question from the user
