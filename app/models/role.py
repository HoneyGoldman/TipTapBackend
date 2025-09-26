from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, ForeignKey, Text, DECIMAL, Boolean, func
from app.models.base import Base


class Role(Base):
    __tablename__ = "role"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey("business.id", ondelete="CASCADE"), nullable=False)
    position = Column(Enum("waiter", "bartender", "barista", "hostess", "shift_manager", name="role_position_enum"), nullable=False)
    payment_per_hour = Column(DECIMAL(10, 2), nullable=False)
    location = Column(String(255), nullable=False)
    when_need = Column(Enum("this_week", "always_looking", name="when_need_enum"), nullable=False)
    experience_required = Column(Enum("no_experience", "some_experience", "experience_only", name="experience_required_enum"), nullable=False)
    shift_morning = Column(Boolean, nullable=False, default=False)
    shift_evening = Column(Boolean, nullable=False, default=False)
    shift_weekends = Column(Boolean, nullable=False, default=False)
    shift_full_time = Column(Boolean, nullable=False, default=False)
    shift_part_time = Column(Boolean, nullable=False, default=False)
    about_job = Column(Text, nullable=True)
    min_hourly_wage = Column(DECIMAL(10, 2), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


class RoleLike(Base):
    __tablename__ = "role_like"
    role_id = Column(BigInteger, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)


