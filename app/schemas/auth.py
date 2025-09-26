from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.business import BusinessType


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    timeout_token: str


class ManagerRegisterRequest(BaseModel):
    display_name: str
    email: EmailStr
    password: str
    business_name: str
    business_location: str
    business_type: BusinessType
    menu_url: Optional[str] = None
