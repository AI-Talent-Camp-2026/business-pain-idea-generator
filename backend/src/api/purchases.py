from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from ..models import get_db, Purchase, Idea
from ..config import settings, logger

router = APIRouter()


class CreatePurchaseRequest(BaseModel):
    idea_id: int


@router.post("/purchases")
async def create_purchase(
    request: Request,
    purchase_data: CreatePurchaseRequest,
    db: Session = Depends(get_db)
):
    """Record a purchase (button click) for an idea"""
    try:
        # Get idea to validate it exists
        idea = db.query(Idea).filter(Idea.id == purchase_data.idea_id).first()
        if not idea:
            raise HTTPException(status_code=404, detail="Идея не найдена")

        # Get user IP and user agent
        user_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:500]

        # Create purchase record
        purchase = Purchase(
            idea_id=purchase_data.idea_id,
            run_id=idea.run_id,
            user_ip=user_ip,
            user_agent=user_agent
        )

        db.add(purchase)
        db.commit()
        db.refresh(purchase)

        logger.info(f"Purchase recorded: idea_id={purchase_data.idea_id}, ip={user_ip}")

        return {
            "success": True,
            "message": "Спасибо, запрос отправлен.",
            "purchase_id": purchase.id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating purchase: {e}")
        raise HTTPException(status_code=500, detail="Ошибка записи покупки")


@router.get("/admin/purchases")
async def get_purchases_stats(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """Get purchase statistics (protected endpoint)"""
    # Simple API key authentication
    if api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Неверный API ключ")

    try:
        # Total purchases count
        total_purchases = db.query(func.count(Purchase.id)).scalar()

        # Recent purchases (last 50)
        recent_purchases = db.query(Purchase).order_by(
            Purchase.created_at.desc()
        ).limit(50).all()

        # Top ideas by purchases
        top_ideas = db.query(
            Idea.id,
            Idea.title,
            func.count(Purchase.id).label('purchase_count')
        ).join(Purchase).group_by(Idea.id).order_by(
            func.count(Purchase.id).desc()
        ).limit(10).all()

        return {
            "total_purchases": total_purchases,
            "recent_purchases": [p.to_dict() for p in recent_purchases],
            "top_ideas": [
                {
                    "idea_id": idea_id,
                    "title": title,
                    "purchase_count": count
                }
                for idea_id, title, count in top_ideas
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching purchase stats: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")
