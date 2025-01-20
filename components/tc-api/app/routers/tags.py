from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_active_user
from app.models.tag import Tag, TagCreate, TagUpdate, TagList
from app.models.user import User
from app.services.tag_service import TagService

router = APIRouter()

@router.post("/", response_model=Tag, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_active_user),
    tag_service: TagService = Depends()
) -> Any:
    """Create a new tag."""
    try:
        return await tag_service.create_tag(tag, current_user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
async def get_tags(
    skip: int = 0,
    limit: int = 10,
    tag_service: TagService = Depends()
) -> Any:
    """Get all tags with pagination."""
    tags = await tag_service.get_tags(skip=skip, limit=limit)
    total = await tag_service.count_tags()
    return {
        "items": tags,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{name}", response_model=Tag)
async def get_tag(
    name: str,
    tag_service: TagService = Depends()
) -> Any:
    """Get a specific tag by name."""
    tag = await tag_service.get_tag_by_name(name)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag

@router.put("/{name}", response_model=Tag)
async def update_tag(
    name: str,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    tag_service: TagService = Depends()
) -> Any:
    """Update a tag by name. If tag name is changed, all tagged solutions will be updated."""
    try:
        # If name is being updated, check if new name already exists
        if tag_update.name and tag_update.name != name:
            existing_tag = await tag_service.get_tag_by_name(tag_update.name)
            if existing_tag:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tag name '{tag_update.name}' already exists"
                )
        
        # Update tag and all solutions using it
        tag = await tag_service.update_tag_by_name(
            name=name,
            tag_update=tag_update,
            username=current_user.username,
            update_solutions=True  # This flag tells the service to update solutions
        )
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tag: {str(e)}"
        )

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    name: str,
    current_user: User = Depends(get_current_active_user),
    tag_service: TagService = Depends()
) -> None:
    """Delete a tag by name."""
    try:
        success = await tag_service.delete_tag_by_name(name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
