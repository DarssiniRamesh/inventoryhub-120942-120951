from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransferBase(BaseModel):
    source_storeroom_id: Optional[int] = Field(None, description="Source storeroom ID")
    destination_storeroom_id: Optional[int] = Field(None, description="Destination storeroom ID")
    item_id: int = Field(..., description="Item ID")
    quantity: int = Field(..., gt=0, description="Quantity to transfer")
    transfer_type: str = Field(..., description="Transfer type: transfer, adjustment, receive, issue")
    reason: Optional[str] = Field(None, max_length=200, description="Reason for transfer")
    notes: Optional[str] = Field(None, description="Additional notes")

class TransferCreate(TransferBase):
    pass

class TransferUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Transfer status")
    notes: Optional[str] = Field(None, description="Additional notes")

class TransferResponse(TransferBase):
    id: int
    transfer_number: str
    status: str
    source_storeroom: Optional[dict] = None
    destination_storeroom: Optional[dict] = None
    item: Optional[dict] = None
    requester: Optional[dict] = None
    approver: Optional[dict] = None
    completer: Optional[dict] = None
    requested_at: datetime
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransferLogResponse(BaseModel):
    id: int
    transfer_id: int
    action: str
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    user: Optional[dict] = None
    timestamp: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
