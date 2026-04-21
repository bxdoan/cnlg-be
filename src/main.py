"""
CNLG Price Tracker - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

app = FastAPI(
    title="CNLG Price Tracker API",
    description="Backend cho Chrome Extension theo dõi giá cungnhaulamgiau.vn",
    version="1.0.0"
)

# ====================== CORS CONFIG ======================
allowed_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allowed_origins == "*" else allowed_origins.split(","),
    allow_credentials=os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ====================== ROUTES ======================
from src.api.routes import router
app.include_router(router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CNLG Backend is running"}

print("✅ CORS middleware đã được load từ .env")
print(f"   Allowed origins: {allowed_origins}")
