from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# PUBLIC_INTERFACE
@router.post("/login", response_model=schemas.Token, summary="User login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    
    - **username**: User's username
    - **password**: User's password
    
    Returns JWT access token for authenticated requests
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = models.datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Include role information in user response
    user_response = schemas.UserResponse(
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_response
    }

# PUBLIC_INTERFACE
@router.get("/me", response_model=schemas.UserResponse, summary="Get current user")
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Get current authenticated user information
    
    Returns user profile with role information
    """
    return schemas.UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role_id=current_user.role_id,
        is_active=current_user.is_active,
        full_name=current_user.full_name,
        role={"id": current_user.role.id, "name": current_user.role.name, "description": current_user.role.description},
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

# PUBLIC_INTERFACE
@router.post("/logout", summary="User logout")
async def logout(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so this endpoint is mainly for consistency.
    Client should discard the token.
    """
    return {"message": "Successfully logged out"}
