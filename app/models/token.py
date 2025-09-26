from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, ForeignKey
from app.models.base import Base


class TokenRecord(Base):
    __tablename__ = "token_table"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), nullable=False)
    modification_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
