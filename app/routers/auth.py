from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from passlib.hash import pbkdf2_sha256
from app.schemas.auth import LoginRequest, LoginResponse, ManagerRegisterRequest
from app.models.user import UserAccount
from app.models.token import TokenRecord
from app.core.security import create_tokens, decode_token
from app.core.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(UserAccount).where(UserAccount.email == payload.email)).scalar_one_or_none()
    if not user or not pbkdf2_sha256.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    a, r, t = create_tokens(user.id)
    db.execute(insert(TokenRecord).values(user_id=user.id, token=a))
    db.commit()
    return LoginResponse(access_token=a, refresh_token=r, timeout_token=t)


@router.post("/register", response_model=LoginResponse)
def register(payload: LoginRequest, db: Session = Depends(get_db)):
    existing = db.execute(select(UserAccount).where(UserAccount.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(400, detail="Email exists")
    user = UserAccount(
        email=payload.email,
        password_hash=pbkdf2_sha256.hash(payload.password),
        display_name=payload.email.split("@")[0],
        user_type="waiter",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    a, r, t = create_tokens(user.id)
    db.execute(insert(TokenRecord).values(user_id=user.id, token=a))
    db.commit()
    return LoginResponse(access_token=a, refresh_token=r, timeout_token=t)


@router.post("/register-manager", response_model=LoginResponse)
def register_manager(payload: ManagerRegisterRequest, db: Session = Depends(get_db)):
    existing = db.execute(select(UserAccount).where(UserAccount.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(400, detail="Email exists")
    user = UserAccount(
        email=payload.email,
        password_hash=pbkdf2_sha256.hash(payload.password),
        display_name=payload.display_name,
        user_type="business_manager",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # Create initial business for manager
    from app.models.business import Business
    biz = Business(
        manager_user_id=user.id,
        name=payload.business_name,
        location=payload.business_location,
        business_type=payload.business_type,
        menu_url=payload.menu_url,
    )
    db.add(biz)
    db.commit()
    a, r, t = create_tokens(user.id)
    db.execute(insert(TokenRecord).values(user_id=user.id, token=a))
    db.commit()
    return LoginResponse(access_token=a, refresh_token=r, timeout_token=t)


def extract_authorization_header(request: Request) -> str:
    hdr = request.headers.get("Authorization")
    if not hdr:
        raise HTTPException(401, detail="Missing Authorization header")
    if not hdr.startswith("Bearer "):
        raise HTTPException(401, detail="Invalid Authorization header")
    return hdr.split(" ", 1)[1]
