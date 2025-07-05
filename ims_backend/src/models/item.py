from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    sku = Column(String(50), unique=True, index=True)
    category = Column(String(50), index=True)
    unit_of_measure = Column(String(20), default="pcs")
    minimum_stock = Column(Integer, default=0)
    maximum_stock = Column(Integer)
    unit_cost = Column(Numeric(10, 2))
    barcode = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    storeroom_items = relationship("StoreroomItem", back_populates="item")
    transfers = relationship("Transfer", back_populates="item")
