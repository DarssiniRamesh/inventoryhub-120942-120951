from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Storeroom(Base):
    __tablename__ = "storerooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(200))
    location = Column(String(200))
    capacity = Column(Integer)
    manager_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("User", back_populates="managed_storerooms")
    storeroom_items = relationship("StoreroomItem", back_populates="storeroom")
    source_transfers = relationship("Transfer", foreign_keys="Transfer.source_storeroom_id", back_populates="source_storeroom")
    destination_transfers = relationship("Transfer", foreign_keys="Transfer.destination_storeroom_id", back_populates="destination_storeroom")
