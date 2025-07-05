from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/storerooms", tags=["Storerooms"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.StoreroomResponse], summary="Get all storerooms")
async def get_storerooms(
    skip: int = Query(0, ge=0, description="Number of storerooms to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of storerooms to return"),
    search: Optional[str] = Query(None, description="Search term for name or location"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all storerooms with optional filtering and pagination
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search in name, description, location
    - **is_active**: Filter by active status
    
    Requires authentication.
    """
    query = db.query(models.Storeroom).join(models.User, models.Storeroom.manager_id == models.User.id, isouter=True)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Storeroom.name.like(search_filter)) |
            (models.Storeroom.description.like(search_filter)) |
            (models.Storeroom.location.like(search_filter))
        )
    
    if is_active is not None:
        query = query.filter(models.Storeroom.is_active == is_active)
    
    storerooms = query.offset(skip).limit(limit).all()
    
    return [
        schemas.StoreroomResponse(
            id=storeroom.id,
            name=storeroom.name,
            description=storeroom.description,
            location=storeroom.location,
            capacity=storeroom.capacity,
            manager_id=storeroom.manager_id,
            is_active=storeroom.is_active,
            manager={"id": storeroom.manager.id, "username": storeroom.manager.username, "full_name": storeroom.manager.full_name} if storeroom.manager else None,
            created_at=storeroom.created_at,
            updated_at=storeroom.updated_at
        ) for storeroom in storerooms
    ]

# PUBLIC_INTERFACE
@router.get("/{storeroom_id}", response_model=schemas.StoreroomResponse, summary="Get storeroom by ID")
async def get_storeroom(
    storeroom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific storeroom by ID
    
    - **storeroom_id**: Storeroom ID to retrieve
    
    Requires authentication.
    """
    storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == storeroom_id).first()
    if not storeroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storeroom not found")
    
    return schemas.StoreroomResponse(
        id=storeroom.id,
        name=storeroom.name,
        description=storeroom.description,
        location=storeroom.location,
        capacity=storeroom.capacity,
        manager_id=storeroom.manager_id,
        is_active=storeroom.is_active,
        manager={"id": storeroom.manager.id, "username": storeroom.manager.username, "full_name": storeroom.manager.full_name} if storeroom.manager else None,
        created_at=storeroom.created_at,
        updated_at=storeroom.updated_at
    )

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.StoreroomResponse, summary="Create new storeroom")
async def create_storeroom(
    storeroom: schemas.StoreroomCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new storeroom
    
    - **name**: Unique storeroom name
    - **description**: Storeroom description
    - **location**: Physical location
    - **capacity**: Storage capacity
    - **manager_id**: Manager user ID
    - **is_active**: Whether storeroom is active
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Check if name already exists
    if db.query(models.Storeroom).filter(models.Storeroom.name == storeroom.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Storeroom name already exists")
    
    # Check if manager exists
    if storeroom.manager_id:
        manager = db.query(models.User).filter(models.User.id == storeroom.manager_id).first()
        if not manager:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manager not found")
    
    # Create storeroom
    db_storeroom = models.Storeroom(
        name=storeroom.name,
        description=storeroom.description,
        location=storeroom.location,
        capacity=storeroom.capacity,
        manager_id=storeroom.manager_id,
        is_active=storeroom.is_active
    )
    
    db.add(db_storeroom)
    db.commit()
    db.refresh(db_storeroom)
    
    return schemas.StoreroomResponse(
        id=db_storeroom.id,
        name=db_storeroom.name,
        description=db_storeroom.description,
        location=db_storeroom.location,
        capacity=db_storeroom.capacity,
        manager_id=db_storeroom.manager_id,
        is_active=db_storeroom.is_active,
        manager={"id": db_storeroom.manager.id, "username": db_storeroom.manager.username, "full_name": db_storeroom.manager.full_name} if db_storeroom.manager else None,
        created_at=db_storeroom.created_at,
        updated_at=db_storeroom.updated_at
    )

# PUBLIC_INTERFACE
@router.put("/{storeroom_id}", response_model=schemas.StoreroomResponse, summary="Update storeroom")
async def update_storeroom(
    storeroom_id: int,
    storeroom_update: schemas.StoreroomUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update a storeroom
    
    - **storeroom_id**: Storeroom ID to update
    - **storeroom_update**: Updated storeroom information
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == storeroom_id).first()
    if not storeroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storeroom not found")
    
    # Update fields
    update_data = storeroom_update.dict(exclude_unset=True)
    
    # Check uniqueness constraints
    if "name" in update_data and update_data["name"] != storeroom.name:
        if db.query(models.Storeroom).filter(models.Storeroom.name == update_data["name"]).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Storeroom name already exists")
    
    # Check manager exists
    if "manager_id" in update_data and update_data["manager_id"]:
        manager = db.query(models.User).filter(models.User.id == update_data["manager_id"]).first()
        if not manager:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Manager not found")
    
    # Apply updates
    for field, value in update_data.items():
        setattr(storeroom, field, value)
    
    storeroom.updated_at = models.datetime.utcnow()
    db.commit()
    db.refresh(storeroom)
    
    return schemas.StoreroomResponse(
        id=storeroom.id,
        name=storeroom.name,
        description=storeroom.description,
        location=storeroom.location,
        capacity=storeroom.capacity,
        manager_id=storeroom.manager_id,
        is_active=storeroom.is_active,
        manager={"id": storeroom.manager.id, "username": storeroom.manager.username, "full_name": storeroom.manager.full_name} if storeroom.manager else None,
        created_at=storeroom.created_at,
        updated_at=storeroom.updated_at
    )

# PUBLIC_INTERFACE
@router.delete("/{storeroom_id}", summary="Delete storeroom")
async def delete_storeroom(
    storeroom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete a storeroom
    
    - **storeroom_id**: Storeroom ID to delete
    
    Requires admin privileges.
    """
    # Check permissions
    if current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == storeroom_id).first()
    if not storeroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storeroom not found")
    
    # Check if storeroom has items
    if db.query(models.StoreroomItem).filter(models.StoreroomItem.storeroom_id == storeroom_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete storeroom with items")
    
    db.delete(storeroom)
    db.commit()
    
    return {"message": "Storeroom deleted successfully"}

# PUBLIC_INTERFACE
@router.get("/{storeroom_id}/items", response_model=List[schemas.StoreroomItemResponse], summary="Get storeroom items")
async def get_storeroom_items(
    storeroom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all items in a specific storeroom
    
    - **storeroom_id**: Storeroom ID
    
    Requires authentication.
    """
    storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == storeroom_id).first()
    if not storeroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storeroom not found")
    
    storeroom_items = db.query(models.StoreroomItem).filter(models.StoreroomItem.storeroom_id == storeroom_id).all()
    
    return [
        schemas.StoreroomItemResponse(
            id=item.id,
            storeroom_id=item.storeroom_id,
            item_id=item.item_id,
            quantity=item.quantity,
            reserved_quantity=item.reserved_quantity,
            available_quantity=item.available_quantity,
            storeroom={"id": item.storeroom.id, "name": item.storeroom.name},
            item={"id": item.item.id, "name": item.item.name, "sku": item.item.sku, "unit_of_measure": item.item.unit_of_measure},
            last_counted_at=item.last_counted_at,
            last_updated_at=item.last_updated_at
        ) for item in storeroom_items
    ]
