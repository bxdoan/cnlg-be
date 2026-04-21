"""
CNLG Price Tracker - Main FastAPI Application
CORS được tối ưu mạnh nhất cho Chrome Extension
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")

# ====================== CORS TỐI ƯU CHO CHROME EXTENSION ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Cho phép chrome-extension://*
    allow_credentials=False,       # ← Quan trọng: Phải False khi dùng *
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,                   # Cache preflight 10 phút
)

# ====================== ROUTES ======================
app.include_router(router, prefix="/api")

# ====================== HEALTH CHECK ======================
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "CNLG Backend is running - CORS FIXED for Extension"
    }

# ====================== STARTUP ======================
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend đã chạy - CORS đã fix cho Chrome Extension")

print("🚀 CNLG Backend started with STRONG CORS for chrome-extension://*")