from typing import List, Literal, Optional
from pydantic import BaseModel


class TokenData(BaseModel):
    user_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    user_id: str

class UserInDB(User):
    hashed_password: str

class Content(BaseModel):
    role: Literal["user", "model"]
    parts: List[str]

class ChatHistory(BaseModel):
    content: List[Content]