from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StoreroomItem(Base):
    __tablename__ = "storeroom_items"
    
    id = Column(Integer, primary_key=True, index=True)
    storeroom_id = Column(Integer, ForeignKey("storerooms.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    last_counted_at = Column(DateTime)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    storeroom = relationship("Storeroom", back_populates="storeroom_items")
    item = relationship("Item", back_populates="storeroom_items")
    
    # Constraints
    __table_args__ = (UniqueConstraint('storeroom_id', 'item_id', name='unique_storeroom_item'),)
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
