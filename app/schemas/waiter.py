from pydantic import BaseModel, Field
from typing import Annotated
from typing import List, Optional, Literal

Status = Literal['pre_army', 'post_army', 'student', 'other']
LookingFor = Literal['waiter','bartender','barista','hostess','shift_manager','manager']
HourTag = Literal['part_time','full_time','morning','evening','weekends']
ExpTag = Literal['waiter','barman','barista','shift_manager','host']
SayTag = Literal['best_coffee_maker','good_vibe','best_cocktails','customers_love_me']
SkillTag = Literal['customer_service','basic_computer','coffee_making','teamwork','food_service','working_under_pressure','table_management']


class WaiterCreate(BaseModel):
    display_name: str
    email: str
    password: Annotated[str, Field(max_length=72)]
    status: Status
    looking_for: List[LookingFor] = []
    about_me: Optional[str] = None
    distance_km: Optional[int] = None
    min_hourly_wage: Optional[float] = None
    shifts_per_week: Optional[int] = None
    hours: List[HourTag] = Field(default_factory=list)
    experience: List[ExpTag] = Field(default_factory=list)
    people_say: List[SayTag] = Field(default_factory=list)
    skills: List[SkillTag] = Field(default_factory=list)


class WaiterOut(BaseModel):
    user_id: int
    display_name: str
    email: str
    status: Status
    looking_for: List[LookingFor] = []
    about_me: Optional[str] = None
    distance_km: Optional[int] = None
    min_hourly_wage: Optional[float] = None
    shifts_per_week: Optional[int] = None
    hours: List[HourTag] = Field(default_factory=list)
    experience: List[ExpTag] = Field(default_factory=list)
    people_say: List[SayTag] = Field(default_factory=list)
    skills: List[SkillTag] = Field(default_factory=list)


class WaiterUpdate(BaseModel):
    display_name: Optional[str] = None
    status: Optional[Status] = None
    looking_for: List[LookingFor] = Field(default_factory=list)
    about_me: Optional[str] = None
    distance_km: Optional[int] = None
    min_hourly_wage: Optional[float] = None
    shifts_per_week: Optional[int] = None
    hours: List[HourTag] = Field(default_factory=list)
    experience: List[ExpTag] = Field(default_factory=list)
    people_say: List[SayTag] = Field(default_factory=list)
    skills: List[SkillTag] = Field(default_factory=list)