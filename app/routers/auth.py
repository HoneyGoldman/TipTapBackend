from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from passlib.hash import pbkdf2_sha256
from app.schemas.auth import LoginRequest, LoginResponse, ManagerRegisterRequest, UserOut, RefreshRequest, Tokens
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
    ue = get_user_entity(user.id)
    return LoginResponse(
        access_token=a,
        refresh_token=r,
        timeout_token=t,
        user_entity=UserOut(
            id=ue.id,
            email=ue.email,
            display_name=ue.display_name,
            user_type=ue.user_type,
            is_active=ue.is_active,
        ),
    )


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
    ue = get_user_entity(user.id)
    return LoginResponse(
        access_token=a,
        refresh_token=r,
        timeout_token=t,
        user_entity=UserOut(
            id=ue.id,
            email=ue.email,
            display_name=ue.display_name,
            user_type=ue.user_type,
            is_active=ue.is_active,
        ),
    )


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
    from app.models.business import Business, BusinessManager
    biz = Business(
        name=payload.business_name,
        location=payload.business_location,
        business_type=payload.business_type,
        menu_url=payload.menu_url,
    )
    db.add(biz)
    db.commit()
    db.add(BusinessManager(business_id=biz.id, manager_user_id=user.id))
    db.commit()
    a, r, t = create_tokens(user.id)
    db.execute(insert(TokenRecord).values(user_id=user.id, token=a))
    db.commit()
    ue = get_user_entity(user.id)
    return LoginResponse(
        access_token=a,
        refresh_token=r,
        timeout_token=t,
        user_entity=UserOut(
            id=ue.id,
            email=ue.email,
            display_name=ue.display_name,
            user_type=ue.user_type,
            is_active=ue.is_active,
        ),
    )


@router.post("/refresh", response_model=Tokens)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)):
    # Verify the provided refresh token
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    if data.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(data.get("sub"))
    # Ensure the user exists and is active
    user = db.execute(select(UserAccount).where(UserAccount.id == user_id, UserAccount.is_active == True)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Optional: enforce token rotation by storing refresh tokens; here we just rotate regardless
    a, r, t = create_tokens(user_id)
    # Persist the new access token record (matching login behavior)
    db.execute(insert(TokenRecord).values(user_id=user_id, token=a))
    db.commit()
    return Tokens(access_token=a, refresh_token=r, timeout_token=t)


def extract_authorization_header(request: Request) -> str:
    hdr = request.headers.get("Authorization")
    if not hdr:
        raise HTTPException(401, detail="Missing Authorization header")
    if not hdr.startswith("Bearer "):
        raise HTTPException(401, detail="Invalid Authorization header")
    return hdr.split(" ", 1)[1]


def get_user_entity(user_id: int) -> UserAccount:
    """
    Fetch a `UserAccount` by id using a short-lived session.
    Kept local to avoid circular dependencies between modules.
    """
    # Local import to avoid broad module import side-effects
    from app.models.base import SessionLocal

    with SessionLocal() as session:
        user = session.get(UserAccount, user_id)
        if not user:
            raise HTTPException(404, detail="User not found")
        return user
