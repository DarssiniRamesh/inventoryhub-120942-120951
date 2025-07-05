from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StoreroomItemBase(BaseModel):
    storeroom_id: int = Field(..., description="Storeroom ID")
    item_id: int = Field(..., description="Item ID")
    quantity: int = Field(0, ge=0, description="Quantity")
    reserved_quantity: int = Field(0, ge=0, description="Reserved quantity")

class StoreroomItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0, description="Quantity")
    reserved_quantity: Optional[int] = Field(None, ge=0, description="Reserved quantity")

class StoreroomItemResponse(StoreroomItemBase):
    id: int
    available_quantity: int
    storeroom: Optional[dict] = None
    item: Optional[dict] = None
    last_counted_at: Optional[datetime] = None
    last_updated_at: datetime

    class Config:
        from_attributes = True
