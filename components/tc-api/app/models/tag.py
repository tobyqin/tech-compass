from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.common import PyObjectId, AuditModel

class TagBase(BaseModel):
    """Base tag model"""
    name: str = Field(..., description="Tag name")
    description: Optional[str] = Field(None, description="Tag description")

class TagCreate(TagBase):
    """Model for creating a new tag"""
    pass

class TagUpdate(TagBase):
    """Model for updating an existing tag"""
    name: Optional[str] = None
    description: Optional[str] = None

class TagInDB(TagBase, AuditModel):
    """Model for tag in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    usage_count: int = Field(default=0, description="Number of solutions using this tag")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            PyObjectId: str
        }

class Tag(TagInDB):
    """API response model for tag"""
    pass

class TagList(BaseModel):
    """API response model for list of tags"""
    tags: list[Tag]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            PyObjectId: str
        }
