from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, ForeignKey, Text, DECIMAL, Boolean, func, JSON
from app.models.base import Base


class Business(Base):
    __tablename__ = "business"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    menu_url = Column(String(500), nullable=True)
    images = Column(JSON, nullable=True)
    business_type = Column(Enum("bar", "restaurant", "cafe", "hotel", name="business_type_enum"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)



class BusinessManager(Base):
    __tablename__ = "business_manager"
    business_id = Column(BigInteger, ForeignKey("business.id", ondelete="CASCADE"), primary_key=True)
    manager_user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
