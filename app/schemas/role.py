from pydantic import BaseModel
from typing import Optional, Literal


Position = Literal['waiter','bartender','barista','hostess','shift_manager']
WhenNeed = Literal['this_week','always_looking']
ExperienceRequired = Literal['no_experience','some_experience','experience_only']


class RoleCreate(BaseModel):
    business_id: int
    position: Position
    payment_per_hour: float
    location: str
    when_need: WhenNeed
    experience_required: ExperienceRequired
    shift_morning: bool = False
    shift_evening: bool = False
    shift_weekends: bool = False
    shift_full_time: bool = False
    shift_part_time: bool = False
    about_job: Optional[str] = None
    min_hourly_wage: Optional[float] = None
    is_active: bool = True


class RoleUpdate(BaseModel):
    position: Optional[Position] = None
    payment_per_hour: Optional[float] = None
    location: Optional[str] = None
    when_need: Optional[WhenNeed] = None
    experience_required: Optional[ExperienceRequired] = None
    shift_morning: Optional[bool] = None
    shift_evening: Optional[bool] = None
    shift_weekends: Optional[bool] = None
    shift_full_time: Optional[bool] = None
    shift_part_time: Optional[bool] = None
    about_job: Optional[str] = None
    min_hourly_wage: Optional[float] = None
    is_active: Optional[bool] = None


class RoleOut(BaseModel):
    id: int
    business_id: int
    position: Position
    payment_per_hour: float
    location: str
    when_need: WhenNeed
    experience_required: ExperienceRequired
    shift_morning: bool
    shift_evening: bool
    shift_weekends: bool
    shift_full_time: bool
    shift_part_time: bool
    about_job: Optional[str] = None
    min_hourly_wage: Optional[float] = None
    is_active: bool


