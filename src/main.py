"""
CNLG Price Tracker - Main FastAPI Application
FINAL FIX CORS CHO CHROME EXTENSION
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.scheduler import scheduler

app = FastAPI(title="Price Tracker - cungnhaulamgiau.vn")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(https?://cungnhaulamgiau\.vn|chrome-extension://.*)$",
    allow_credentials=True,          # BẮT BUỘC vì dùng Bearer token
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "FINAL CORS ENABLED"}


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Backend chạy với FINAL CUSTOM CORS cho Chrome Extension")


print("🚀 CNLG Backend started with FINAL CORS FIX")