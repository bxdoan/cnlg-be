"""
Database configuration for CNLG Price Tracker
- PostgreSQL connection via SQLAlchemy
- SessionLocal for dependency injection
- Base for all models
- get_db() dependency used in FastAPI routes
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models (User, Product, PriceHistory...)
Base = declarative_base()

def get_db():
    """FastAPI dependency: yields a database session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()