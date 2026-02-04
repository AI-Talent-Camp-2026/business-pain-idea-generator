from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import get_db
from ..services.idea_service import get_idea_detail
from ..config import logger

router = APIRouter()


@router.get("/ideas/{idea_id}")
async def get_idea(idea_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific idea"""
    idea = get_idea_detail(db, idea_id)

    if not idea:
        raise HTTPException(status_code=404, detail="Идея не найдена")

    return idea.to_dict_full()
