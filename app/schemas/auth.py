from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from app.schemas.business import BusinessType


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


UserType = Literal['waiter', 'business_manager']


class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    user_type: UserType
    is_active: bool


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    timeout_token: str
    user_entity: UserOut


class ManagerRegisterRequest(BaseModel):
    display_name: str
    email: EmailStr
    password: str
    business_name: str
    business_location: str
    business_type: BusinessType
    menu_url: Optional[str] = None


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    timeout_token: str


class RefreshRequest(BaseModel):
    refresh_token: str
