from sqlalchemy.orm import Session

from ..models import Idea


def get_idea_detail(db: Session, idea_id: int) -> Idea:
    """Get full idea details with analogues and evidence"""
    return db.query(Idea).filter(Idea.id == idea_id).first()
