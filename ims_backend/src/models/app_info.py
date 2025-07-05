from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from ..database import Base

class AppInfo(Base):
    __tablename__ = "app_info"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
