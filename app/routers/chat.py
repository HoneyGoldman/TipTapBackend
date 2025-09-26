from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from typing import List
from app.core.deps import get_db, AuthUser
from app.models.chat import Conversation, ConversationParticipant, Message
from app.schemas.chat import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from sqlalchemy import func

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationOut, dependencies=[Depends(AuthUser)])
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    participant_ids = set(payload.participant_user_ids) | {user.id}
    if len(participant_ids) < 2:
        raise HTTPException(400, "Need at least two participants")

    conv = Conversation()
    db.add(conv)
    db.flush()  # get conv.id

    for uid in participant_ids:
        db.add(ConversationParticipant(conversation_id=conv.id, user_id=uid))
    db.commit()

    return ConversationOut(id=conv.id, participant_user_ids=list(participant_ids))


@router.get("/conversations", response_model=List[ConversationOut], dependencies=[Depends(AuthUser)])
def list_conversations(db: Session = Depends(get_db), user=Depends(AuthUser)):
    q = (
        select(ConversationParticipant.conversation_id)
        .where(ConversationParticipant.user_id == user.id)
    )
    conv_ids = [row[0] for row in db.execute(q).all()]

    if not conv_ids:
        return []

    # fetch participants per conversation
    out = []
    for cid in conv_ids:
        p = db.execute(
            select(ConversationParticipant.user_id).where(ConversationParticipant.conversation_id == cid)
        ).all()
        out.append(ConversationOut(id=cid, participant_user_ids=[r[0] for r in p]))
    return out


@router.post("/messages", response_model=MessageOut, dependencies=[Depends(AuthUser)])
def send_message(payload: MessageCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # ensure user is a participant
    part = db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == payload.conversation_id,
            ConversationParticipant.user_id == user.id
        )
    ).scalar_one_or_none()
    if not part:
        raise HTTPException(403, "Not in conversation")

    msg = Message(conversation_id=payload.conversation_id, sender_user_id=user.id, body=payload.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageOut(
        id=msg.id, conversation_id=msg.conversation_id, sender_user_id=msg.sender_user_id,
        body=msg.body, created_at=str(msg.created_at), read_at=(str(msg.read_at) if msg.read_at else None)
    )


@router.get("/messages", response_model=List[MessageOut], dependencies=[Depends(AuthUser)])
def list_messages(conversation_id: int = Query(...), db: Session = Depends(get_db), user=Depends(AuthUser)):
    # ensure user is a participant
    part = db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user.id
        )
    ).scalar_one_or_none()
    if not part:
        raise HTTPException(403, "Not in conversation")

    msgs = db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    ).scalars().all()

    return [
        MessageOut(
            id=m.id, conversation_id=m.conversation_id, sender_user_id=m.sender_user_id,
            body=m.body, created_at=str(m.created_at), read_at=(str(m.read_at) if m.read_at else None)
        )
        for m in msgs
    ]


@router.post("/messages/{message_id}/read", dependencies=[Depends(AuthUser)])
def mark_read(message_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # user must be in the conversation of the message
    msg = db.execute(select(Message).where(Message.id == message_id)).scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")

    part = db.execute(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == msg.conversation_id,
            ConversationParticipant.user_id == user.id
        )
    ).scalar_one_or_none()
    if not part:
        raise HTTPException(403, "Not in conversation")

    db.execute(update(Message).where(Message.id == message_id, Message.read_at.is_(None)).values(read_at=func.now()))
    db.commit()
    return {"ok": True}
