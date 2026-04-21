"""
CNLG Price Tracker API - Full JWT Auth (Register + Login + Protected Routes)
Dựa trên code mới nhất trên GitHub
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Header
from sqlalchemy.orm import Session
from typing import Dict, Any
from src.database import get_db
from src.models import User, PriceHistory
from src.scraper import scrape_all_products
from src.auth import create_access_token, get_password_hash, verify_password, get_current_user
from datetime import datetime, timedelta

router = APIRouter(tags=["auth", "price"])


# ==================== REGISTER ====================
@router.post("/auth/register")
async def register(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        plan="Free",
        weekly_quota=3,
        requests_this_week=0,
        last_quota_reset=datetime.utcnow(),
        max_skus=10
    )
    db.add(user)
    db.commit()
    return {"message": "Đăng ký thành công! Vui lòng đăng nhập."}


# ==================== LOGIN ====================
@router.post("/auth/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "plan": user.plan
    }


# ==================== PROTECTED: HISTORY ====================
@router.get("/history/{sku}")
async def get_price_history(
    sku: str,
    days: int = 30,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu hoặc token không hợp lệ")

    token = authorization.split(" ")[1]
    user = get_current_user(token, db)

    cutoff = datetime.utcnow() - timedelta(days=days)
    history = db.query(PriceHistory).filter(
        PriceHistory.sku == sku,
        PriceHistory.timestamp >= cutoff
    ).order_by(PriceHistory.timestamp.desc()).limit(200).all()

    if not history:
        return {"sku": sku, "message": "Chưa có dữ liệu giá"}

    return {
        "sku": sku,
        "current_price": history[0].current_price,
        "history_count": len(history),
        "plan": user.plan,
        "data": [{"timestamp": h.timestamp.isoformat(), "price": h.current_price} for h in history]
    }


# ==================== PROTECTED: TRIGGER CRAWL ====================
@router.post("/track")
async def track_product(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu hoặc token không hợp lệ")

    token = authorization.split(" ")[1]
    get_current_user(token, db)

    scrape_all_products()
    return {"message": "Crawl toàn bộ sản phẩm thành công"}