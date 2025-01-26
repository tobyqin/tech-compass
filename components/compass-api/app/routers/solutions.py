import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.core.auth import get_current_active_user
from app.models.solution import Solution, SolutionCreate, SolutionUpdate
from app.models.user import User
from app.models.response import StandardResponse
from app.services.solution_service import SolutionService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=StandardResponse[Solution], status_code=status.HTTP_201_CREATED)
async def create_solution(
    solution: SolutionCreate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Create a new solution."""
    try:
        result = await solution_service.create_solution(solution, current_user.username)
        return StandardResponse.of(result)
    except Exception as e:
        logger.error(f"Error creating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating solution: {str(e)}")

@router.get("/", response_model=StandardResponse[List[Solution]])
async def get_solutions(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    department: Optional[str] = None,
    team: Optional[str] = None,
    recommend_status: Optional[str] = Query(None, description="Filter by recommendation status (BUY/HOLD/SELL)"),
    radar_status: Optional[str] = Query(None, description="Filter by radar status (ADOPT/TRIAL/ASSESS/HOLD)"),
    stage: Optional[str] = Query(None, description="Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)"),
    sort: str = Query("name", description="Sort field (prefix with - for descending order)"),
    solution_service: SolutionService = Depends()
) -> Any:
    """Get all solutions with pagination, filtering and sorting.
    
    Query Parameters:
    - category: Filter by category name
    - department: Filter by department name
    - team: Filter by team name
    - recommend_status: Filter by recommendation status (BUY/HOLD/SELL)
    - radar_status: Filter by radar status (ADOPT/TRIAL/ASSESS/HOLD)
    - stage: Filter by stage (DEVELOPING/UAT/PRODUCTION/DEPRECATED/RETIRED)
    - sort: Sort field (name, category, created_at, updated_at). Prefix with - for descending order
    """
    try:
        # Validate enum values if provided
        if recommend_status and recommend_status not in ["BUY", "HOLD", "SELL"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid recommend_status. Must be one of: BUY, HOLD, SELL"
            )
        if radar_status and radar_status not in ["ADOPT", "TRIAL", "ASSESS", "HOLD"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid radar_status. Must be one of: ADOPT, TRIAL, ASSESS, HOLD"
            )
        if stage and stage not in ["DEVELOPING", "UAT", "PRODUCTION", "DEPRECATED", "RETIRED"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid stage. Must be one of: DEVELOPING, UAT, PRODUCTION, DEPRECATED, RETIRED"
            )

        solutions = await solution_service.get_solutions(
            skip=skip,
            limit=limit,
            category=category,
            department=department,
            team=team,
            recommend_status=recommend_status,
            radar_status=radar_status,
            stage=stage,
            sort=sort
        )
        total = await solution_service.count_solutions()
        return StandardResponse.paginated(
            data=solutions,
            total=total,
            skip=skip,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing solutions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing solutions: {str(e)}")

@router.get("/departments", response_model=StandardResponse[List[str]], tags=["solutions"])
async def get_departments(
    solution_service: SolutionService = Depends()
):
    """
    Get all unique department names from solutions.
    
    Returns:
    - items: List of unique department names
    - total: Total number of unique departments
    """
    try:
        departments = await solution_service.get_departments()
        return StandardResponse.paginated(departments, len(departments), 0, 0)
    except Exception as e:
        logger.error(f"Error getting departments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting departments: {str(e)}")

@router.get("/{slug}", response_model=StandardResponse[Solution])
async def get_solution(
    slug: str,
    solution_service: SolutionService = Depends()
) -> Any:
    """Get a specific solution by slug."""
    solution = await solution_service.get_solution_by_slug(slug)
    if not solution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
    return StandardResponse.of(solution)

@router.put("/{slug}", response_model=StandardResponse[Solution])
async def update_solution(
    slug: str,
    solution_update: SolutionUpdate,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> Any:
    """Update a solution by slug."""
    try:
        solution = await solution_service.update_solution_by_slug(slug, solution_update, current_user.username)
        if not solution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solution not found"
            )
        return StandardResponse.of(solution)
    except Exception as e:
        logger.error(f"Error updating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating solution: {str(e)}")

@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_solution(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends()
) -> None:
    """Delete a solution by slug."""
    success = await solution_service.delete_solution_by_slug(slug)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solution not found"
        )
