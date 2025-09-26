from sqlalchemy import Column, BigInteger, String, Enum, Boolean, TIMESTAMP, func, ForeignKey
from app.models.base import Base


class UserAccount(Base):
    __tablename__ = "user_account"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    user_type = Column(Enum("waiter", "business_manager", name="user_type_enum"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(),
                        nullable=False)


class ManagerLikeWaiter(Base):
    __tablename__ = "manager_like_waiter"
    manager_user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    waiter_user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)