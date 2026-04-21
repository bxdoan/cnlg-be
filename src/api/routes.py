from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from src.database import SessionLocal, get_db
from src.models import User, PriceHistory
from src.auth import get_password_hash, get_current_user
from src.scraper import scrape_all_products
from datetime import datetime, timedelta
import uuid

router = APIRouter()


# Đăng ký user
@router.post("/register")
async def register(email: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Email đã tồn tại")
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        plan="Free",
        max_skus=10
    )
    db.add(user)
    db.commit()
    return {"message": "Đăng ký thành công. Chuyển khoản và liên hệ admin để kích hoạt."}


# Admin tạo API Key (bạn dùng)
@router.post("/admin/activate")
async def admin_activate(
        email: str = Body(...),
        plan: str = Body(...),  # Basic, Pro, Enterprise
        months: int = Body(1),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User không tồn tại")

    api_key = f"cnlg_{uuid.uuid4().hex[:16]}"
    user.api_key = api_key
    user.plan = plan
    user.max_skus = {"Basic": 500, "Pro": 10000, "Enterprise": 1000000}[plan]
    user.subscription_end = datetime.utcnow() + timedelta(days=30 * months)
    db.commit()

    return {
        "api_key": api_key,
        "plan": plan,
        "hết hạn": user.subscription_end.strftime("%d/%m/%Y %H:%M")
    }


# API cho Extension
@router.get("/history/{sku}")
async def get_price_history(
        sku: str,
        days: int = 30,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    max_days = 90 if user.plan in ["Pro", "Enterprise"] else 30
    if days > max_days: days = max_days
    cutoff = datetime.utcnow() - timedelta(days=days)

    history = db.query(PriceHistory).filter(
        PriceHistory.sku == sku,
        PriceHistory.timestamp >= cutoff
    ).order_by(PriceHistory.timestamp).all()

    if not history:
        return {"message": "Chưa có dữ liệu"}

    min_price = min(h.current_price for h in history)
    return {
        "sku": sku,
        "current_price": history[-1].current_price,
        "retail_price": history[-1].retail_price,
        "min_price": min_price,
        "savings_percent": round((history[-1].current_price - min_price) / history[-1].current_price * 100, 1),
        "history": [{"timestamp": h.timestamp.isoformat(), "price": h.current_price} for h in history]
    }


@router.post("/track")
async def track_product(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await scrape_all_products()
    return {"message": "Đã thêm sản phẩm"}