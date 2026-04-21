from passlib.context import CryptContext
from fastapi import HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

from src.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(api_key: str = Header(None, alias="X-API-Key"), db: Session = None):
    if not api_key:
        raise HTTPException(status_code=401, detail="Thiếu X-API-Key")
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="API Key không hợp lệ")
    if user.subscription_end and user.subscription_end < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Gói đã hết hạn")
    return user