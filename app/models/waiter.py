from sqlalchemy import Column, BigInteger, String, Enum, Integer, Text, DECIMAL, TIMESTAMP, ForeignKey, func
from app.models.base import Base


class WaiterProfile(Base):
    __tablename__ = "waiter_profile"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    status = Column(Enum("pre_army", "post_army", "student", "other", name="waiter_status_enum"), nullable=False)
    about_me = Column(Text, nullable=True)
    distance_km = Column(Integer, nullable=True)
    min_hourly_wage = Column(DECIMAL(10, 2), nullable=True)
    shifts_per_week = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


class WaiterLookingFor(Base):
    __tablename__ = "waiter_looking_for"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    looking_for = Column(Enum("waiter", "bartender", "barista", "hostess", "shift_manager", "manager", name="looking_for_enum"), primary_key=True)


class WaiterHours(Base):
    __tablename__ = "waiter_hours"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    hour_tag = Column(Enum("part_time", "full_time", "morning", "evening", "weekends", name="waiter_hour_tag_enum"), primary_key=True)


class WaiterExperience(Base):
    __tablename__ = "waiter_experience"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    exp_tag = Column(Enum("waiter", "barman", "barista", "shift_manager", "host", name="waiter_exp_tag_enum"), primary_key=True)


class WaiterPeopleSay(Base):
    __tablename__ = "waiter_people_say"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    say_tag = Column(Enum("best_coffee_maker", "good_vibe", "best_cocktails", "customers_love_me", name="waiter_say_tag_enum"), primary_key=True)


class WaiterSkills(Base):
    __tablename__ = "waiter_skills"
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    skill_tag = Column(Enum("customer_service", "basic_computer", "coffee_making", "teamwork", "food_service", "working_under_pressure", "table_management", name="waiter_skill_tag_enum"), primary_key=True)


