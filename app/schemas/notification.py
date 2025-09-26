from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any


NotificationType = Literal[
    'upcoming_interview',
    'new_match',
    'business_liked_you',
    'interview_succeeded',
    'arriving_for_shift',
    'new_message'
]


class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    payload: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    payload: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[str] = None
    created_at: Optional[str] = None
    read_at: Optional[str] = None


