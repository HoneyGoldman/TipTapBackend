from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, ForeignKey, Text, JSON, DateTime, func
from app.models.base import Base


class Notification(Base):
    __tablename__ = "notification"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(
        "upcoming_interview",
        "new_match",
        "business_liked_you",
        "interview_succeeded",
        "arriving_for_shift",
        "new_message",
        name="notification_type_enum"
    ), nullable=False)
    payload = Column(JSON, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    read_at = Column(DateTime, nullable=True)


