from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.services.bug_service import validate_and_create_bug, ValidationError

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
