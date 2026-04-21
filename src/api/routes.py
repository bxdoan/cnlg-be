"""
CNLG Price Tracker - FastAPI Routes
Minimal & stable version to start server successfully.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from src.database import get_db
from src.models import User, PriceHistory
from src.scraper import scrape_all_products
from datetime import datetime, timedelta
import uuid

router = APIRouter()

# ==================== TEMPORARY STUB FOR AUTH ====================
# (Chúng ta sẽ implement auth thật sau khi server chạy ổn)
def get_current_user():
    """Temporary dummy user for testing. Replace later with real API Key / JWT."""
    class DummyUser:
        id = 1
        email = "test@example.com"
        plan = "Pro"
        api_key = "dummy_key_for_testing"
    return DummyUser()


# ==================== HEALTH CHECK ====================
@router.get("/health")
async def health_check():
    """Simple health check - confirm API is running."""
    return {"status": "ok", "message": "CNLG Price Tracker API is running"}


# ==================== PRICE HISTORY ====================
@router.get("/history/{sku}", response_model=None)
async def get_price_history(
    sku: str,
    days: int = 30,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get price history for a product (30 days default, max 90 for Pro)."""
    # Simple query for now
    cutoff = datetime.utcnow() - timedelta(days=days)
    history = db.query(PriceHistory).filter(
        PriceHistory.sku == sku,
        PriceHistory.timestamp >= cutoff
    ).order_by(PriceHistory.timestamp.desc()).limit(100).all()

    if not history:
        return {"sku": sku, "message": "No price history yet"}

    return {
        "sku": sku,
        "current_price": history[0].current_price,
        "history_count": len(history),
        "plan": current_user.plan,
        "data": [{"timestamp": h.timestamp.isoformat(), "price": h.current_price} for h in history]
    }


# ==================== TRIGGER CRAWL ====================
@router.post("/track", response_model=None)
async def track_product(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger full site crawl (for testing)."""
    try:
        scrape_all_products()
        return {"message": "Full crawl completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REGISTER (for future use) ====================
@router.post("/register")
async def register(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    # TODO: add full registration later
    return {"message": "User registered (admin needs to activate)"}