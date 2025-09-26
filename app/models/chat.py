from sqlalchemy import Column, BigInteger, TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Conversation(Base):
    __tablename__ = "conversation"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    participants = relationship("ConversationParticipant", cascade="all, delete-orphan", backref="conversation", lazy="selectin")


class ConversationParticipant(Base):
    __tablename__ = "conversation_participant"
    conversation_id = Column(BigInteger, ForeignKey("conversation.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)


class Message(Base):
    __tablename__ = "message"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    read_at = Column(TIMESTAMP, nullable=True)