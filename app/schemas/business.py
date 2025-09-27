from pydantic import BaseModel, EmailStr
from typing import Optional, Literal, List


BusinessType = Literal['bar','restaurant','cafe','hotel']


class BusinessCreate(BaseModel):
    name: str
    location: str
    business_type: BusinessType
    menu_url: Optional[str] = None
    images: Optional[List[str]] = None
    manager_user_ids: Optional[List[int]] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    business_type: Optional[BusinessType] = None
    menu_url: Optional[str] = None
    images: Optional[List[str]] = None


class BusinessOut(BaseModel):
    id: int
    manager_user_ids: List[int]
    name: str
    location: str
    business_type: BusinessType
    menu_url: Optional[str] = None
    images: Optional[List[str]] = None


class AddManagerRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


