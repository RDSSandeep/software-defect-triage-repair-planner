from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.services.bug_service import validate_and_create_bug, ValidationError, get_all_bugs, get_bug_by_id

router = APIRouter(prefix="/api/bugs", tags=["Bugs"])

class BugCreateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    environment: Optional[str] = None
    steps: Optional[str] = None

@router.post("", status_code=status.HTTP_201_CREATED)
def submit_bug(request: BugCreateRequest):
    try:
        bug = validate_and_create_bug(
            title=request.title,
            description=request.description,
            environment=request.environment,
            steps=request.steps
        )
        return bug
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", status_code=status.HTTP_200_OK)
def list_bugs():
    return get_all_bugs()

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_bug(id: str):
    bug = get_bug_by_id(id)
    if bug is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug with ID {id} not found"
        )
    return bug
