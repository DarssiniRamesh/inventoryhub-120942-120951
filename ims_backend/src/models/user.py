from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    permissions = Column(Text)  # JSON string of permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    managed_storerooms = relationship("Storeroom", back_populates="manager")
    requested_transfers = relationship("Transfer", foreign_keys="Transfer.requested_by", back_populates="requester")
    approved_transfers = relationship("Transfer", foreign_keys="Transfer.approved_by", back_populates="approver")
    completed_transfers = relationship("Transfer", foreign_keys="Transfer.completed_by", back_populates="completer")
    transfer_logs = relationship("TransferLog", back_populates="user")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
