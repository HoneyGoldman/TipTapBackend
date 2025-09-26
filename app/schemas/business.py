from pydantic import BaseModel
from typing import Optional, Literal


BusinessType = Literal['bar','restaurant','cafe','hotel']


class BusinessCreate(BaseModel):
    name: str
    location: str
    business_type: BusinessType
    menu_url: Optional[str] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    business_type: Optional[BusinessType] = None
    menu_url: Optional[str] = None


class BusinessOut(BaseModel):
    id: int
    manager_user_id: int
    name: str
    location: str
    business_type: BusinessType
    menu_url: Optional[str] = None


