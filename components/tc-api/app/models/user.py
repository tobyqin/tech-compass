from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.common import AuditModel, PyObjectId

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="Username for login")
    full_name: str = Field(..., description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., description="User's password (will be hashed)")

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDB(UserBase, AuditModel):
    """User model as stored in database"""
    hashed_password: str = Field(..., description="Hashed password")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class User(UserInDB):
    """User model for API responses"""
    pass
