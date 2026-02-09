"""
Authentication routes: login, token refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.schemas import LoginRequest, TokenResponse
from app.models.models import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User/Admin login endpoint
    Validates credentials and returns JWT tokens with role information
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email, User.is_active == True).first()
    
    print(user)
    
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    token_data = {"sub": str(user.id), "role": user.role.name}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.name,
        user_id=user.id,
        name=user.name
    )
