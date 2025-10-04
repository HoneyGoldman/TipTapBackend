from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.models.base import SessionLocal
from app.core.security import decode_token
from app.models.token import TokenRecord
from app.models.user import UserAccount
from typing import Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_token(token: str, db: Session) -> UserAccount:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(payload.get("sub", 0))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid subject")

    # Enforce presence in token_table
    rec = db.execute(
        select(TokenRecord).where(TokenRecord.user_id == user_id, TokenRecord.token == token)
    ).scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=401, detail="Token not registered")

    user = db.execute(select(UserAccount).where(UserAccount.id == user_id)).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user

def AuthUser(request: Request, db: Session = Depends(get_db)):
    # Parse Authorization header directly
    hdr = request.headers.get("Authorization")
    if not hdr or not hdr.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = hdr.split(" ", 1)[1]
    return require_token(token, db)


def OptionalAuth(request: Request, db: Session = Depends(get_db)) -> Optional[UserAccount]:
    """
    Attempt to authenticate; return None if missing/invalid token.
    Do NOT raise; authorization will be enforced by callers as needed.
    """
    hdr = request.headers.get("Authorization")
    if not hdr or not hdr.startswith("Bearer "):
        return None
    token = hdr.split(" ", 1)[1]
    try:
        return require_token(token, db)
    except Exception:
        return None
