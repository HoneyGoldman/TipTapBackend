from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings


def _encode(payload: dict, exp_minutes: int):
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)


def create_tokens(user_id: int):
    access_token = _encode({"sub": str(user_id), "typ": "access"}, settings.access_minutes)
    refresh_token = _encode({"sub": str(user_id), "typ": "refresh"}, settings.refresh_days * 24 * 60)
    timeout_token = _encode({"sub": str(user_id), "typ": "timeout"}, settings.timeout_minutes)
    return access_token, refresh_token, timeout_token


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
