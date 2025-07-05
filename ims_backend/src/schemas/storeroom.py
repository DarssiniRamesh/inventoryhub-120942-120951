from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StoreroomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Storeroom name")
    description: Optional[str] = Field(None, max_length=200, description="Description")
    location: Optional[str] = Field(None, max_length=200, description="Location")
    capacity: Optional[int] = Field(None, ge=0, description="Capacity")
    manager_id: Optional[int] = Field(None, description="Manager user ID")
    is_active: bool = Field(True, description="Storeroom is active")

class StoreroomCreate(StoreroomBase):
    pass

class StoreroomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Storeroom name")
    description: Optional[str] = Field(None, max_length=200, description="Description")
    location: Optional[str] = Field(None, max_length=200, description="Location")
    capacity: Optional[int] = Field(None, ge=0, description="Capacity")
    manager_id: Optional[int] = Field(None, description="Manager user ID")
    is_active: Optional[bool] = Field(None, description="Storeroom is active")

class StoreroomResponse(StoreroomBase):
    id: int
    manager: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
