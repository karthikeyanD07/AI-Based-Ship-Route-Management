"""Authentication routes."""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.models.database import User, get_db
from backend.app.auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    require_auth
)
from backend.app.auth.models import UserCreate, UserLogin, Token, UserResponse
from backend.app.config.settings import settings
from backend.app.utils.audit_logger import audit_logger
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        roles_json = json.dumps(user_data.roles)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            roles=roles_json,
            is_active=1
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Audit log
        audit_logger.log_action(
            action="user_register",
            request=request,
            username=user_data.username,
            resource="user",
            resource_id=str(db_user.id),
            status_code=201
        )
        
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            roles=json.loads(db_user.roles) if db_user.roles else [],
            created_at=db_user.created_at,
            is_active=bool(db_user.is_active)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Login and get access token."""
    try:
        # Find user
        user = db.query(User).filter(User.username == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            audit_logger.log_action(
                action="login_failed",
                request=request,
                username=form_data.username,
                status_code=401
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create token
        roles = json.loads(user.roles) if user.roles else []
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "roles": roles}
        )
        
        # Audit log
        audit_logger.log_action(
            action="login_success",
            request=request,
            user_id=user.id,
            username=user.username,
            status_code=200
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(require_auth), db: Session = Depends(get_db)):
    """Get current user information."""
    user_id = int(user["sub"])
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        roles=json.loads(db_user.roles) if db_user.roles else [],
        created_at=db_user.created_at,
        is_active=bool(db_user.is_active)
    )
