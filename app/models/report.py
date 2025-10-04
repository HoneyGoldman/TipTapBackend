from sqlalchemy import Column, BigInteger, String, JSON, TIMESTAMP, func
from app.models.base import Base


class ReportConfiguration(Base):
    __tablename__ = "report_configuration"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_name = Column(String(255), unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)
    procedure_name = Column(String(255), nullable=False)
    is_active = Column(BigInteger, nullable=False, default=1)
    authorized_required = Column(BigInteger, nullable=False, default=1)
    creation_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    modification_date = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


