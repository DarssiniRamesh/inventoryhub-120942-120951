from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.UserResponse], summary="Get all users")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    search: Optional[str] = Query(None, description="Search term for username, email, or name"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all users with optional filtering and pagination
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search in username, email, first_name, last_name
    - **role_id**: Filter by specific role
    - **is_active**: Filter by active status
    
    Requires authentication. Admins can see all users, others see limited info.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    query = db.query(models.User).join(models.Role)
    
    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.User.username.like(search_filter)) |
            (models.User.email.like(search_filter)) |
            (models.User.first_name.like(search_filter)) |
            (models.User.last_name.like(search_filter))
        )
    
    if role_id is not None:
        query = query.filter(models.User.role_id == role_id)
    
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    
    return [
        schemas.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role_id=user.role_id,
            is_active=user.is_active,
            full_name=user.full_name,
            role={"id": user.role.id, "name": user.role.name, "description": user.role.description},
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        ) for user in users
    ]

# PUBLIC_INTERFACE
@router.get("/{user_id}", response_model=schemas.UserResponse, summary="Get user by ID")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific user by ID
    
    - **user_id**: User ID to retrieve
    
    Requires authentication. Users can view their own profile, admins can view any user.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"] and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role_id=user.role_id,
        is_active=user.is_active,
        full_name=user.full_name,
        role={"id": user.role.id, "name": user.role.name, "description": user.role.description},
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.UserResponse, summary="Create new user")
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new user
    
    - **username**: Unique username
    - **email**: Unique email address
    - **password**: User password
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role_id**: Role ID for the user
    - **is_active**: Whether user is active
    
    Requires admin privileges.
    """
    # Check permissions
    if current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Check if username already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    # Check if role exists
    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    
    # Create user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role_id=user.role_id,
        is_active=user.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return schemas.UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        role_id=db_user.role_id,
        is_active=db_user.is_active,
        full_name=db_user.full_name,
        role={"id": db_user.role.id, "name": db_user.role.name, "description": db_user.role.description},
        last_login=db_user.last_login,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )

# PUBLIC_INTERFACE
@router.put("/{user_id}", response_model=schemas.UserResponse, summary="Update user")
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Update a user
    
    - **user_id**: User ID to update
    - **user_update**: Updated user information
    
    Users can update their own profile, admins can update any user.
    """
    # Check permissions
    if current_user.role.name != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle password update
    if "password" in update_data:
        update_data["password_hash"] = auth.get_password_hash(update_data.pop("password"))
    
    # Check uniqueness constraints
    if "username" in update_data and update_data["username"] != user.username:
        if db.query(models.User).filter(models.User.username == update_data["username"]).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    if "email" in update_data and update_data["email"] != user.email:
        if db.query(models.User).filter(models.User.email == update_data["email"]).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    # Check role exists
    if "role_id" in update_data:
        role = db.query(models.Role).filter(models.Role.id == update_data["role_id"]).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")
    
    # Apply updates
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = models.datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role_id=user.role_id,
        is_active=user.is_active,
        full_name=user.full_name,
        role={"id": user.role.id, "name": user.role.name, "description": user.role.description},
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

# PUBLIC_INTERFACE
@router.delete("/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete a user
    
    - **user_id**: User ID to delete
    
    Requires admin privileges. Cannot delete self.
    """
    # Check permissions
    if current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
