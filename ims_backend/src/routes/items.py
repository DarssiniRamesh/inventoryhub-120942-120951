from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/items", tags=["Items"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.ItemResponse], summary="Get all items")
async def get_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search term for name, SKU, or category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all items with optional filtering and pagination
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search in name, description, SKU, category
    - **category**: Filter by specific category
    - **is_active**: Filter by active status
    
    Requires authentication.
    """
    query = db.query(models.Item)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Item.name.like(search_filter)) |
            (models.Item.description.like(search_filter)) |
            (models.Item.sku.like(search_filter)) |
            (models.Item.category.like(search_filter))
        )
    
    if category:
        query = query.filter(models.Item.category == category)
    
    if is_active is not None:
        query = query.filter(models.Item.is_active == is_active)
    
    items = query.offset(skip).limit(limit).all()
    
    return [
        schemas.ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            sku=item.sku,
            category=item.category,
            unit_of_measure=item.unit_of_measure,
            minimum_stock=item.minimum_stock,
            maximum_stock=item.maximum_stock,
            unit_cost=item.unit_cost,
            barcode=item.barcode,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at
        ) for item in items
    ]

# PUBLIC_INTERFACE
@router.get("/{item_id}", response_model=schemas.ItemResponse, summary="Get item by ID")
async def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific item by ID
    
    - **item_id**: Item ID to retrieve
    
    Requires authentication.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return schemas.ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        sku=item.sku,
        category=item.category,
        unit_of_measure=item.unit_of_measure,
        minimum_stock=item.minimum_stock,
        maximum_stock=item.maximum_stock,
        unit_cost=item.unit_cost,
        barcode=item.barcode,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at
    )

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.ItemResponse, summary="Create new item")
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new item
    
    - **name**: Item name
    - **description**: Item description
    - **sku**: Stock keeping unit (unique)
    - **category**: Item category
    - **unit_of_measure**: Unit of measure
    - **minimum_stock**: Minimum stock level
    - **maximum_stock**: Maximum stock level
    - **unit_cost**: Unit cost
    - **barcode**: Barcode
    - **is_active**: Whether item is active
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Check if SKU already exists
    if item.sku and db.query(models.Item).filter(models.Item.sku == item.sku).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
    
    # Create item
    db_item = models.Item(
        name=item.name,
        description=item.description,
        sku=item.sku,
        category=item.category,
        unit_of_measure=item.unit_of_measure,
        minimum_stock=item.minimum_stock,
        maximum_stock=item.maximum_stock,
        unit_cost=item.unit_cost,
        barcode=item.barcode,
        is_active=item.is_active
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return schemas.ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        sku=db_item.sku,
        category=db_item.category,
        unit_of_measure=db_item.unit_of_measure,
        minimum_stock=db_item.minimum_stock,
        maximum_stock=db_item.maximum_stock,
        unit_cost=db_item.unit_cost,
        barcode=db_item.barcode,
        is_active=db_item.is_active,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

# PUBLIC_INTERFACE
@router.put("/{item_id}", response_model=schemas.ItemResponse, summary="Update item")
async def update_item(
    item_id: int,
    item_update: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update an item
    
    - **item_id**: Item ID to update
    - **item_update**: Updated item information
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    
    # Check SKU uniqueness
    if "sku" in update_data and update_data["sku"] != item.sku:
        if db.query(models.Item).filter(models.Item.sku == update_data["sku"]).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU already exists")
    
    # Apply updates
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = models.datetime.utcnow()
    db.commit()
    db.refresh(item)
    
    return schemas.ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        sku=item.sku,
        category=item.category,
        unit_of_measure=item.unit_of_measure,
        minimum_stock=item.minimum_stock,
        maximum_stock=item.maximum_stock,
        unit_cost=item.unit_cost,
        barcode=item.barcode,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at
    )

# PUBLIC_INTERFACE
@router.delete("/{item_id}", summary="Delete item")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete an item
    
    - **item_id**: Item ID to delete
    
    Requires admin privileges.
    """
    # Check permissions
    if current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Check if item is in use
    if db.query(models.StoreroomItem).filter(models.StoreroomItem.item_id == item_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete item that is in use")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item deleted successfully"}

# PUBLIC_INTERFACE
@router.get("/{item_id}/inventory", summary="Get item inventory across storerooms")
async def get_item_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get inventory levels for a specific item across all storerooms
    
    - **item_id**: Item ID
    
    Requires authentication.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    storeroom_items = db.query(models.StoreroomItem).filter(models.StoreroomItem.item_id == item_id).all()
    
    return {
        "item_id": item_id,
        "item_name": item.name,
        "total_quantity": sum(si.quantity for si in storeroom_items),
        "total_available": sum(si.available_quantity for si in storeroom_items),
        "storerooms": [
            {
                "storeroom_id": si.storeroom_id,
                "storeroom_name": si.storeroom.name,
                "quantity": si.quantity,
                "reserved_quantity": si.reserved_quantity,
                "available_quantity": si.available_quantity,
                "last_updated": si.last_updated_at
            } for si in storeroom_items
        ]
    }
