from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List
from app.core.deps import get_db, AuthUser
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationOut


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut], dependencies=[Depends(AuthUser)])
def list_notifications(db: Session = Depends(get_db), user=Depends(AuthUser)):
    rows = db.execute(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())).scalars().all()
    return [
        NotificationOut(
            id=n.id,
            user_id=n.user_id,
            type=n.type,
            payload=n.payload,
            scheduled_at=(n.scheduled_at.isoformat() if n.scheduled_at else None),
            created_at=str(n.created_at),
            read_at=(n.read_at.isoformat() if n.read_at else None)
        ) for n in rows
    ]


@router.post("/", response_model=NotificationOut, dependencies=[Depends(AuthUser)])
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # Allow creating notifications for self only (or later: admins/managers for others)
    if payload.user_id != user.id:
        raise HTTPException(403, "Cannot create for other users")
    n = Notification(user_id=payload.user_id, type=payload.type, payload=payload.payload)
    db.add(n)
    db.commit()
    db.refresh(n)
    return NotificationOut(
        id=n.id, user_id=n.user_id, type=n.type, payload=n.payload,
        scheduled_at=(n.scheduled_at.isoformat() if n.scheduled_at else None),
        created_at=str(n.created_at), read_at=(n.read_at.isoformat() if n.read_at else None)
    )


@router.post("/{notification_id}/read", dependencies=[Depends(AuthUser)])
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    n = db.execute(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id)).scalar_one_or_none()
    if not n:
        raise HTTPException(404, "Not found")
    db.execute(update(Notification).where(Notification.id == notification_id).values(read_at=None))
    # Properly set read_at to NOW()
    from sqlalchemy import func
    db.execute(update(Notification).where(Notification.id == notification_id).values(read_at=func.now()))
    db.commit()
    return {"ok": True}


@router.delete("/{notification_id}", dependencies=[Depends(AuthUser)])
def delete_notification(notification_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    n = db.execute(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id)).scalar_one_or_none()
    if not n:
        raise HTTPException(404, "Not found")
    db.execute(delete(Notification).where(Notification.id == notification_id))
    db.commit()
    return {"ok": True}


