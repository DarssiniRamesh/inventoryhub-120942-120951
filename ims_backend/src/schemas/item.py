from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    sku: Optional[str] = Field(None, max_length=50, description="SKU")
    category: Optional[str] = Field(None, max_length=50, description="Category")
    unit_of_measure: str = Field("pcs", max_length=20, description="Unit of measure")
    minimum_stock: int = Field(0, ge=0, description="Minimum stock level")
    maximum_stock: Optional[int] = Field(None, ge=0, description="Maximum stock level")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode")
    is_active: bool = Field(True, description="Item is active")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    sku: Optional[str] = Field(None, max_length=50, description="SKU")
    category: Optional[str] = Field(None, max_length=50, description="Category")
    unit_of_measure: Optional[str] = Field(None, max_length=20, description="Unit of measure")
    minimum_stock: Optional[int] = Field(None, ge=0, description="Minimum stock level")
    maximum_stock: Optional[int] = Field(None, ge=0, description="Maximum stock level")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode")
    is_active: Optional[bool] = Field(None, description="Item is active")

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
