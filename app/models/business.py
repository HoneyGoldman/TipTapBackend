from sqlalchemy import Column, BigInteger, String, Enum, TIMESTAMP, ForeignKey, Text, DECIMAL, Boolean, func
from app.models.base import Base


class Business(Base):
    __tablename__ = "business"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    manager_user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    menu_url = Column(String(500), nullable=True)
    business_type = Column(Enum("bar", "restaurant", "cafe", "hotel", name="business_type_enum"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


