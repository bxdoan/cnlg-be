from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean
from datetime import datetime
from src.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    api_key = Column(String, unique=True, nullable=True)
    plan = Column(String, default="Free")  # Free, Basic, Pro, Enterprise

    # NEW: Weekly quota (reset every week, billing still monthly)
    weekly_quota = Column(Integer, default=3)  # Free: 3, Pro: 300, ...
    requests_this_week = Column(Integer, default=0)
    last_quota_reset = Column(DateTime, nullable=True)

    max_skus = Column(Integer, default=10)
    subscription_end = Column(DateTime, nullable=True)


class Product(Base):
    __tablename__ = "products"
    sku = Column(String, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)

    # NEW: Thumbnail image for user display / Chrome Extension
    thumbnail_url = Column(String, nullable=True)

    last_crawled = Column(DateTime, default=datetime.utcnow)


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, ForeignKey("products.sku"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    retail_price = Column(BigInteger, nullable=True)
    original_price = Column(BigInteger, nullable=True)
    current_price = Column(BigInteger)

    discount_percent = Column(Integer, nullable=True)