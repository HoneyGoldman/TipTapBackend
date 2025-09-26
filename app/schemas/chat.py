from pydantic import BaseModel
from typing import List, Optional


class ConversationCreate(BaseModel):
    participant_user_ids: List[int]  # include the caller as well or we’ll add it server-side


class ConversationOut(BaseModel):
    id: int
    participant_user_ids: List[int]


class MessageCreate(BaseModel):
    conversation_id: int
    body: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_user_id: int
    body: str
    created_at: str
    read_at: Optional[str] = None
