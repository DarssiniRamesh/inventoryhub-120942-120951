from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String(50), unique=True, nullable=False, index=True)
    source_storeroom_id = Column(Integer, ForeignKey("storerooms.id"))
    destination_storeroom_id = Column(Integer, ForeignKey("storerooms.id"))
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    transfer_type = Column(String(20), nullable=False)  # 'transfer', 'adjustment', 'receive', 'issue'
    status = Column(String(20), default='pending')  # 'pending', 'in_transit', 'completed', 'cancelled'
    reason = Column(String(200))
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    completed_by = Column(Integer, ForeignKey("users.id"))
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    source_storeroom = relationship("Storeroom", foreign_keys=[source_storeroom_id], back_populates="source_transfers")
    destination_storeroom = relationship("Storeroom", foreign_keys=[destination_storeroom_id], back_populates="destination_transfers")
    item = relationship("Item", back_populates="transfers")
    requester = relationship("User", foreign_keys=[requested_by], back_populates="requested_transfers")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_transfers")
    completer = relationship("User", foreign_keys=[completed_by], back_populates="completed_transfers")
    transfer_logs = relationship("TransferLog", back_populates="transfer")

class TransferLog(Base):
    __tablename__ = "transfer_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    action = Column(String(20), nullable=False)  # 'created', 'approved', 'in_transit', 'completed', 'cancelled'
    previous_status = Column(String(20))
    new_status = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    transfer = relationship("Transfer", back_populates="transfer_logs")
    user = relationship("User", back_populates="transfer_logs")
