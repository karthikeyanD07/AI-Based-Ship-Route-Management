"""Authentication models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    roles: List[str] = Field(default_factory=lambda: ["viewer"])


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    roles: List[str]
    created_at: datetime
    is_active: bool = True
